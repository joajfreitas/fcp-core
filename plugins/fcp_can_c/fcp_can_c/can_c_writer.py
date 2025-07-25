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

from beartype.typing import (
    Any,
    Generator,
    List,
    Dict,
    Optional,
    Tuple,
    Union,
    cast,
    Set,
)
from math import ceil
from jinja2 import Environment, FileSystemLoader
from fcp.specs.struct_field import StructField
from fcp.specs.v2 import FcpV2
from fcp.specs.service import Service
from dataclasses import dataclass
from fcp.encoding import make_encoder, EncodeablePiece, Value, PackedEncoderContext
from fcp.utils import to_pascal_case, to_snake_case


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
        self.name_snake = to_snake_case(self.name_pascal)

        for signal in self.signals:
            if signal.is_multiplexer:
                self.multiplexer_signal = to_snake_case(signal.multiplexer_signal)
                self.is_multiplexer = True


@dataclass
class Enum:
    """Class to represent an enum."""

    name: str
    values: Dict[str, int]


class CanNode:
    """Class to represent a device node with RPC compatibility."""

    def __init__(
        self, name: str, rpc_get_id: Union[int, None], rpc_ans_id: Union[int, None]
    ):
        self.name = name
        self.rpc_get_id = rpc_get_id
        self.rpc_ans_id = rpc_ans_id
        self.services: List[str] = []


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
) -> Tuple[
    List[Enum],
    List[CanNode],
    List[CanMessage],
    List[CanMessage],
    List[CanMessage],
    List[Service],
]:
    """Initialize CAN data from an FCP.

    Args:
        fcp: FcpV2 object.

    Returns:
        Tuple containing a list of enums, messages and devices.

    """
    enums = []
    messages = []
    devices: List["CanNode"] = []
    rpc: List[CanMessage] = []
    rpc_requests: List[CanMessage] = []
    encoder = make_encoder(
        "packed", fcp, PackedEncoderContext().with_unroll_arrays(True)
    )

    for enum in fcp.enums:
        values = {v.name: v.value for v in enum.enumeration}
        enums.append(Enum(name=enum.name, values=values))

    devices.append(CanNode("global", rpc_get_id=None, rpc_ans_id=None))

    device_rpc_info: Dict[str, Dict[str, Optional[int]]] = {}
    device_services: Dict[str, List[str]] = {}
    service_devices: Dict[str, List[str]] = {}
    can_impl_device_by_name: Dict[str, str] = {}
    can_impl_device_by_type: Dict[str, str] = {}
    default_impl_by_name: Dict[str, Any] = {}

    for dev in fcp.devices:
        rpc_get_id: Optional[int] = None
        rpc_ans_id: Optional[int] = None

        protocols = (
            dev.fields.get("protocols") if isinstance(dev.fields, dict) else None
        )
        if isinstance(protocols, dict) and isinstance(protocols.get("can"), dict):
            can_protocol = cast(Dict[str, Any], protocols["can"])

            for impl_binding in cast(
                List[Dict[str, Any]], can_protocol.get("impls", [])
            ):
                binding_name = impl_binding.get("name")
                binding_type = impl_binding.get("type")
                if isinstance(binding_name, str):
                    can_impl_device_by_name.setdefault(binding_name, dev.name)
                if isinstance(binding_type, str):
                    can_impl_device_by_type.setdefault(binding_type, dev.name)

            rpc_block = cast(Dict[str, Any], can_protocol.get("rpc", {}))
            request_id = rpc_block.get("request_id")
            response_id = rpc_block.get("response_id")

            if isinstance(request_id, int):
                rpc_get_id = request_id
            if isinstance(response_id, int):
                rpc_ans_id = response_id

            protocol_fields = cast(Dict[str, Any], can_protocol.get("fields", {}))
            services_from_protocol = protocol_fields.get("services")
            if isinstance(services_from_protocol, list):
                device_services[dev.name] = services_from_protocol

        services_field = dev.fields.get("services")
        if isinstance(services_field, list):
            device_services.setdefault(dev.name, services_field)

        for service_name in device_services.get(dev.name, []):
            service_devices.setdefault(service_name, []).append(dev.name)

        device_rpc_info[dev.name] = {
            "rpc_get_id": rpc_get_id,
            "rpc_ans_id": rpc_ans_id,
        }

    used_devices = {"global"}

    for extension in fcp.impls:
        if extension.protocol == "default":
            default_impl_by_name.setdefault(extension.name, extension)

    for service in fcp.services:
        for method in service.methods:
            method.name_snake = to_snake_case(method.name)
            method.input_snake = to_snake_case(method.input)
            method.output_snake = to_snake_case(method.output)
            # method.unique_id = (service.id << 8) | method.id

    rpc_messages: Set[Tuple[str, int, str]] = set()

    for extension in fcp.get_matching_impls("can"):
        encoding = encoder.generate(extension)
        signals, dlc = create_can_signals(encoding)

        frame_id = extension.fields.get("id")
        period = extension.fields.get("period")

        device_name: Optional[str] = extension.fields.get("device")
        if not isinstance(device_name, str):
            device_name = can_impl_device_by_name.get(extension.name)
        if not isinstance(device_name, str):
            device_name = can_impl_device_by_type.get(extension.type)
        if not isinstance(device_name, str):
            device_name = "global"

        rpc_ids = device_rpc_info.get(device_name, {})
        rpc_get_id = rpc_ids.get("rpc_get_id")
        rpc_ans_id = rpc_ids.get("rpc_ans_id")

        if device_name not in used_devices:
            node = CanNode(device_name, rpc_get_id=rpc_get_id, rpc_ans_id=rpc_ans_id)
            node.services = device_services.get(device_name, [])
            devices.append(node)
            used_devices.add(device_name)

        if frame_id is not None:
            messages.append(
                CanMessage(
                    frame_id=frame_id,
                    name_pascal=extension.name,
                    dlc=dlc,
                    signals=signals,
                    senders=[device_name],
                    period=cast(int, period) if period is not None else -1,
                )
            )

    for service in fcp.services:
        target_devices = service_devices.get(service.name, ["global"])

        for device_name in target_devices:
            rpc_ids = device_rpc_info.get(device_name, {})
            rpc_get_id = rpc_ids.get("rpc_get_id")
            rpc_ans_id = rpc_ids.get("rpc_ans_id")

            if device_name not in used_devices:
                node = CanNode(
                    device_name, rpc_get_id=rpc_get_id, rpc_ans_id=rpc_ans_id
                )
                node.services = device_services.get(device_name, [])
                devices.append(node)
                used_devices.add(device_name)

            for method in service.methods:
                for struct_name, frame_id, direction in (
                    (method.input, rpc_get_id, "request"),
                    (method.output, rpc_ans_id, "response"),
                ):
                    if frame_id is None:
                        continue

                    impl = default_impl_by_name.get(struct_name)
                    if impl is None:
                        impl = next(
                            (ext for ext in fcp.impls if ext.name == struct_name),
                            None,
                        )

                    if impl is None:
                        continue

                    encoding = encoder.generate(impl)
                    signals, dlc = create_can_signals(encoding)

                    key = (struct_name, cast(int, frame_id), direction)
                    if key in rpc_messages:
                        continue

                    message = CanMessage(
                        frame_id=cast(int, frame_id),
                        name_pascal=struct_name,
                        dlc=dlc,
                        signals=signals,
                        senders=[device_name] if direction == "request" else [],
                        period=-1,
                    )

                    rpc.append(message)
                    if direction == "request":
                        rpc_requests.append(message)
                    rpc_messages.add(key)

    return (enums, messages, devices, rpc, rpc_requests, fcp.services)


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

        (
            self.enums,
            self.messages,
            self.devices,
            self.rpcs,
            self.rpc_requests,
            self.services,
        ) = initialize_can_data(fcp)
        self.env = Environment(loader=FileSystemLoader(self.templates_dir))

        self.templates = {
            "device_can_h": self.env.get_template("can_device_h.j2"),
            "device_can_c": self.env.get_template("can_device_c.j2"),
            "device_rpc_h": self.env.get_template("rpc_device_h.j2"),
            "device_rpc_c": self.env.get_template("rpc_device_c.j2"),
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
        global_device_exists = any(device.name == "global" for device in self.devices)

        for device in self.devices:
            device_name = device.name
            messages = self.device_messages.get(device_name, [])

            yield (
                device_name,
                self.templates["device_can_h"].render(
                    device_name_pascal=to_pascal_case(device_name),
                    device_name_snake=to_snake_case(device_name),
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
                to_snake_case(device_name),
                self.templates["device_can_c"].render(
                    device_name_pascal=to_pascal_case(device_name),
                    device_name_snake=to_snake_case(device_name),
                    messages=messages,
                ),
            )

    def generate_rpc_headers(self) -> Generator[Tuple[str, str], None, None]:
        """Generate C header files for devices with RPC.

        Returns:
            Generator: Tuple containing the device name and the file content.

        """
        self._devices_with_rpc = set()

        for device in self.devices:
            if device.rpc_get_id is None or device.rpc_ans_id is None:
                continue

            device_name = device.name

            self._devices_with_rpc.add(device_name)

            yield (
                device_name,
                self.templates["device_rpc_h"].render(
                    device_name_pascal=to_pascal_case(device_name),
                    device_name_snake=to_snake_case(device_name),
                    rpc_get_id=device.rpc_get_id,
                    rpc_ans_id=device.rpc_ans_id,
                    rpcs=self.rpcs,
                    rpc_requests=self.rpc_requests,
                    services=self.services,
                ),
            )

    def generate_rpc_sources(self) -> Generator[Tuple[str, str], None, None]:
        """Generate C source files for devices with RPC.

        Returns:
            Generator: Tuple containing the device name and the file content.

        """
        for device_name, messages in self.device_messages.items():
            if device_name not in self._devices_with_rpc:
                continue

            device = next(d for d in self.devices if d.name == device_name)

            yield (
                to_snake_case(device_name),
                self.templates["device_rpc_c"].render(
                    device_name_pascal=to_pascal_case(device_name),
                    device_name_snake=to_snake_case(device_name),
                    messages=messages,
                    rpc_get_id=device.rpc_get_id,
                    rpc_ans_id=device.rpc_ans_id,
                    rpcs=self.rpcs,
                    rpc_requests=self.rpc_requests,
                    services=self.services,
                ),
            )
