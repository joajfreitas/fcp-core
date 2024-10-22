import os

from pathlib import Path
from beartype.typing import Generator, Tuple, List, Dict, Any, Optional
from math import ceil
from cantools.database import conversion
from jinja2 import Environment, FileSystemLoader
from cantools.database.can.node import Node as CanNode
from fcp.specs import Signal
from fcp import FcpV2
from dataclasses import dataclass
from fcp.result import Result, Ok, Err
from fcp.maybe import catch
from fcp.encoding import make_encoder, EncodeablePiece, Value


def snake_to_pascal(snake_str: str) -> str:
    return "".join(x.capitalize() for x in snake_str.split("_"))


def pascal_to_snake(pascal_str: str) -> str:
    return "".join(["_" + c.lower() if c.isupper() else c for c in pascal_str]).lstrip(
        "_"
    )


@dataclass
class CanSignal:
    name: str
    start_bit: int
    bit_length: int
    data_type: str
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

    def __post_init__(self):
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
        self.multiplexer_count = (
            len(self.multiplexer_ids) if self.multiplexer_ids else 0
        )


@dataclass
class CanMessage:
    frame_id: int
    dlc: int
    signals: List[Signal]
    senders: List[str]
    name_pascal: str
    name_snake: str = ""

    def __post_init__(self):
        self.name_snake = pascal_to_snake(self.name_pascal)

        for signal in self.signals:
            if signal.is_multiplexer:
                self.multiplexer_signal = pascal_to_snake(signal.multiplexer_signal)
                self.is_multiplexer = True


def is_signed(value: Value) -> bool:
    return value.type.startswith("i")


def create_can_signals(encoding: List[EncodeablePiece]) -> Tuple[List[Signal], int]:
    signals = []
    max_dlc = 0

    for piece in encoding:
        multiplexer_signal = piece.extended_data.get("mux_signal")
        multiplexer_ids = list(range(piece.extended_data.get("mux_count", 0)))

        signals.append(
            CanSignal(
                name=piece.name.replace("::", "_"),
                start_bit=piece.bitstart,
                data_type=piece.type,
                bit_length=piece.bitlength,
                byte_order="big_endian"
                if piece.endianess == "big"
                else "little_endian",
                signed=is_signed(piece),
                is_multiplexer=bool(multiplexer_signal),
                multiplexer_ids=multiplexer_ids if multiplexer_signal else None,
                multiplexer_signal=multiplexer_signal,
            )
        )

        max_dlc = max(max_dlc, ceil((piece.bitstart + piece.bitlength) / 8))

    return signals, max_dlc


def map_messages_to_devices(messages: List[CanMessage]) -> Dict[str, List[CanMessage]]:
    device_messages = {}
    for msg in messages:
        for sender in msg.senders:
            device_messages.setdefault(sender, []).append(msg)
    return device_messages


def initialize_can_data(fcp: FcpV2) -> Tuple[List[CanMessage], List[CanNode]]:
    messages = []
    devices = []
    encoder = make_encoder("packed", fcp)

    for extension in fcp.get_matching_extensions("can"):
        encoding = encoder.generate(extension)
        signals, dlc = create_can_signals(encoding)

        frame_id = extension.fields.get("id")
        if frame_id is None:
            return Err("No id field found in extension").unwrap()

        device_name = extension.fields.get("device", "global")

        if not any(node.name == device_name for node in devices):
            devices.append(CanNode(device_name))

        messages.append(
            CanMessage(
                frame_id=frame_id,
                name_pascal=extension.name,
                dlc=dlc,
                signals=signals,
                senders=[device_name],
            )
        )

    return messages, devices


class CanCWriter:
    def __init__(self, fcp: FcpV2) -> None:
        # Get the path to the templates directory
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.templates_dir = os.path.join(script_dir, "../templates")

        self.messages, self.devices = initialize_can_data(fcp)
        self.env = Environment(loader=FileSystemLoader(self.templates_dir))

        self.templates = {
            "device_can_h": self.env.get_template("can_device_h.jinja"),
            "device_can_c": self.env.get_template("can_device_c.jinja"),
        }
        self.device_messages = map_messages_to_devices(self.messages)

    def generate_static_files(self) -> Generator[Tuple[str, str], None, None]:
        """Generate static C files required for CAN."""
        static_files = ["can_frame.h", "can_signal_parser.h", "can_signal_parser.c"]

        for file in static_files:
            with open(f"{self.templates_dir}/{file}", "r") as f:
                yield file, f.read()

    def generate_device_headers(self) -> Generator[Tuple[str, str], None, None]:
        """Generate C header files for devices."""
        for device_name, messages in self.device_messages.items():
            yield (
                device_name,
                self.templates["device_can_h"].render(
                    device_name_pascal=snake_to_pascal(device_name),
                    device_name_snake=pascal_to_snake(device_name),
                    messages=messages,
                ),
            )

    def generate_device_sources(self) -> Generator[Tuple[str, str], None, None]:
        """Generate C source file for the device."""
        for device_name, messages in self.device_messages.items():
            yield (
                pascal_to_snake(device_name),
                self.templates["device_can_c"].render(
                    device_name_pascal=snake_to_pascal(device_name),
                    device_name_snake=pascal_to_snake(device_name),
                    messages=messages,
                ),
            )
