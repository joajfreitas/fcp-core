# Copyright (c) 2024 the fcp AUTHORS.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""CAN C writer module."""

import os

from pathlib import Path
from beartype.typing import Generator, List, Dict, Any, Optional, Tuple, Union
from math import ceil
from jinja2 import Environment, FileSystemLoader
from fcp.specs.struct_field import StructField
from fcp.specs.v2 import FcpV2
from dataclasses import dataclass
from fcp.result import Err
from fcp.encoding import make_encoder, EncodeablePiece, Value, PackedEncoderContext


def snake_to_pascal(snake_str: str) -> str:
    """Convert a snake_case string to PascalCase.

    Args:
        snake_str: The snake_case string to convert.

    Returns:
        The PascalCase string.

    """
    return "".join(x.capitalize() for x in snake_str.split("_"))


def pascal_to_snake(pascal_str: str) -> str:
    """Convert a PascalCase string to snake_case.

    Args:
        pascal_str: The PascalCase string to convert.

    Returns:
        The snake_case string.

    """
    return "".join(["_" + c.lower() if c.isupper() else c for c in pascal_str]).lstrip(
        "_"
    )


def ceil_to_power_of_2(x: int) -> int:
    """Ceil a number to the next power of 2.

    Args:
        x: The number to ceil.

    Returns:
        The next power of 2 starting from 8.

    """
    if x <= 8:
        return 8

    x -= 1
    x |= x >> 1
    x |= x >> 2
    x |= x >> 4
    x |= x >> 8
    x |= x >> 16
    x |= x >> 32

    return x + 1


@dataclass
class CanSignal:
    """A signal in a CAN message (data)."""

    name: str
    start_bit: int
    bit_length: int
    data_type: str  # user defined data type
    scalar_type: str  # (u8, i12...)
    signed: bool
    byte_order: str
    scale: float = 1.0
    offset: float = 0.0
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    unit: Optional[str] = None
    comment: Optional[str] = None
    is_multiplexer: bool = False
    multiplexer_ids: Optional[List[int]] = None
    multiplexer_signal: Optional[str] = None
    is_big_endian_s: str = "False"

    def __post_init__(self) -> None:
        """Post init method to set the scalar type and multiplexer count."""
        type_map = {
            "i8": "int8_t",
            "i16": "int16_t",
            "i32": "int32_t",
            "i64": "int64_t",
            "u8": "uint8_t",
            "u16": "uint16_t",
            "u32": "uint32_t",
            "u64": "uint64_t",
            "f32": "float",
            "f64": "double",
        }

        self.data_type = type_map.get(self.data_type, self.data_type)
        self.is_big_endian_s = "true" if self.byte_order == "big_endian" else "false"

        # If the data type is not in the type map, it is a user defined type or a short type (i12, u5...) so we need to calculate the scalar type
        if self.data_type not in type_map.values():
            self.scalar_type = type_map[
                "i" if self.signed else "u" + str(ceil_to_power_of_2(self.bit_length))
            ]
        else:
            self.scalar_type = self.data_type

        self.multiplexer_count = (
            len(self.multiplexer_ids) if self.multiplexer_ids else 0
        )


@dataclass
class CanMessage:
    """Class to represent a CAN message."""

    frame_id: int
    dlc: int
    signals: List[StructField]
    senders: List[str]
    name_pascal: str
    period: int
    name_snake: str = ""

    def __post_init__(self) -> None:
        self.name_snake = pascal_to_snake(self.name_pascal)

        for signal in self.signals:
            if signal.is_multiplexer:
                self.multiplexer_signal = pascal_to_snake(signal.multiplexer_signal)
                self.is_multiplexer = True


@dataclass
class Enum:
    """Class to represent an enum."""

    name: str
    values: Dict[str, int]


class CanNode:
    """Represents a device node with RPC compatibility."""

    def __init__(
        self, name: str, rpc_get: "Union[int, None]", rpc_ans: "Union[int, None]"
    ):
        self.name = name
        self.rpc_get = rpc_get
        self.rpc_ans = rpc_ans


def is_signed(value: Value) -> bool:
    """Check if a value is signed.

    Args:
        value (Value): Value to check

    Returns:
        bool: True if the value is signed, False otherwise

    """
    return bool(value.type.name.startswith("i"))


def create_can_signals(
    encoding: List[EncodeablePiece],
) -> Tuple[List[StructField], int]:
    """Create a list of CAN signals from a list of EncodeablePieces.

    Args:
        encoding: List of EncodeablePieces to create signals from.

    Returns:
        Tuple containing a list of CAN signals and the maximum DLC.

    """
    signals = []
    max_dlc = 0

    for piece in encoding:
        multiplexer_signal = piece.extended_data.get("mux_signal")
        multiplexer_ids = list(range(piece.extended_data.get("mux_count", 0)))

        type = piece.composite_type.unwrap_or(piece.type.name)
        signals.append(
            CanSignal(
                name=piece.name.replace("::", "_"),
                start_bit=piece.bitstart,
                data_type=type,
                scalar_type=piece.type.name,
                bit_length=piece.bitlength,
                byte_order=(
                    "big_endian"
                    if piece.extended_data.get("endianness", "little") == "big"
                    else "little_endian"
                ),
                signed=is_signed(piece),
                is_multiplexer=bool(multiplexer_signal),
                multiplexer_ids=multiplexer_ids if multiplexer_signal else None,
                multiplexer_signal=multiplexer_signal,
            )
        )

        max_dlc = max(max_dlc, ceil((piece.bitstart + piece.bitlength) / 8))

    return signals, max_dlc


def map_messages_to_devices(messages: List[CanMessage]) -> Dict[str, List[CanMessage]]:
    """Map messages to devices based on the senders.

    Args:
        messages: List of messages to map.

    Returns:
        Dict: Mapping of devices to messages.

    """
    device_messages = {}  # type: ignore
    for msg in messages:
        for sender in msg.senders:
            device_messages.setdefault(sender, []).append(msg)
    return device_messages


def initialize_can_data(
    fcp: FcpV2,
) -> Tuple[List[Enum], List[CanMessage], List[CanNode]]:  # type: ignore
    """Initialize CAN data from an FCP.

    Args:
        fcp: FcpV2 object.

    Returns:
        Tuple containing a list of enums, messages and devices.

    """
    enums = []
    messages = []
    devices: List["CanNode"] = []
    encoder = make_encoder(
        "packed", fcp, PackedEncoderContext().with_unroll_arrays(True)
    )

    for enum in fcp.enums:
        values = {v.name: v.value for v in enum.enumeration}
        enums.append(Enum(name=enum.name, values=values))

        # Enums are not tied to a specific device so they live on the global device
        devices.append(CanNode("global", rpc_get=None, rpc_ans=None))

    for extension in fcp.get_matching_impls("can"):
        encoding = encoder.generate(extension)
        signals, dlc = create_can_signals(encoding)

        frame_id = extension.fields.get("id")
        if frame_id is None:
            Err("No id field found in extension").unwrap()

        device_name = extension.fields.get("device", "global")
        period = extension.fields.get("period", -1)

        if not any(node.name == device_name for node in devices):
            devices.append(CanNode(device_name, rpc_get=None, rpc_ans=None))

        messages.append(
            CanMessage(
                frame_id=frame_id,
                name_pascal=extension.name,
                dlc=dlc,
                signals=signals,
                senders=[device_name],
                period=period,
            )
        )

    return (enums, messages, devices)


class CanCWriter:
    """Class to generate C files for CAN devices."""

    def __init__(self, fcp: FcpV2) -> None:
        """Initialize the CanCWriter.

        Args:
            fcp: FcpV2 object.

        """
        # Get the path to the templates directory
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.templates_dir = os.path.join(script_dir, "../templates")

        self.enums, self.messages, self.devices = initialize_can_data(fcp)
        self.env = Environment(loader=FileSystemLoader(self.templates_dir))

        self.templates = {
            "device_can_h": self.env.get_template("can_device_h.jinja"),
            "device_can_c": self.env.get_template("can_device_c.jinja"),
        }
        self.device_messages = map_messages_to_devices(self.messages)

    def generate_static_files(self) -> Generator[Tuple[str, str], None, None]:
        """Generate all static C files.

        Returns:
            Generator: Tuple containing the file name and the file content.

        """
        static_files = ["can_frame.h", "can_signal_parser.h", "can_signal_parser.c"]

        for file in static_files:
            with open(f"{self.templates_dir}/{file}", "r") as f:
                yield file, f.read()

    def generate_device_headers(self) -> Generator[Tuple[str, str], None, None]:
        """Generate C header files for devices.

        Returns:
            Generator: Tuple containing the device name and the file content.

        """
        # Check if the global device is present in the list of devices
        global_device_exists = any(device.name == "global" for device in self.devices)

        for device in self.devices:
            device_name = device.name
            messages = self.device_messages.get(device_name, [])

            yield (
                device_name,
                self.templates["device_can_h"].render(
                    device_name_pascal=snake_to_pascal(device_name),
                    device_name_snake=pascal_to_snake(device_name),
                    messages=messages,
                    include_global=device_name != "global" and global_device_exists,
                    is_global_device=device_name == "global",
                    enums=self.enums if device_name == "global" else [],
                ),
            )

    def generate_device_sources(self) -> Generator[Tuple[str, str], None, None]:
        """Generate C source files for devices.

        Returns:
            Generator: Tuple containing the device name and the file content.

        """
        for device_name, messages in self.device_messages.items():
            yield (
                pascal_to_snake(device_name),
                self.templates["device_can_c"].render(
                    device_name_pascal=snake_to_pascal(device_name),
                    device_name_snake=pascal_to_snake(device_name),
                    messages=messages,
                ),
            )
