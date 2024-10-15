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
    components = snake_str.split("_")
    return "".join(x.capitalize() for x in components)


def pascal_to_snake(pascal_str: str) -> str:
    return "".join(["_" + c.lower() if c.isupper() else c for c in pascal_str]).lstrip(
        "_"
    )


@dataclass
class CanSignal:
    name: str
    start: int
    type: str
    length: int
    is_signed: bool
    byte_order: str
    scale: float = 1.0
    offset: float = 0.0
    minimum: Optional[str] = None
    maximum: Optional[str] = None
    unit: Optional[str] = None
    comment: Optional[str] = None
    is_multiplexer: bool = False
    multiplexer_ids: Optional[List[int]] = None
    multiplexer_signal: Optional[str] = None

    def __post_init__(self):
        fcp_to_c_type = {
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

        self.type = fcp_to_c_type.get(self.type, self.type)
        self.sign = "signed" if self.is_signed else "unsigned"


@dataclass
class CanMessage:
    frame_id: int
    length: int
    signals: List[Signal]
    senders: List[str]
    name: str  # PascalCase msg name
    name_sc: str = ""  # snake_case msg name

    def __post_init__(self):
        self.name_sc = pascal_to_snake(self.name)


def is_signed(value: Value) -> bool:
    """Determine if the value is signed based on its type."""
    return value.type.startswith("i")


def make_signals(encoding: List[EncodeablePiece]) -> Tuple[List[Signal], int]:
    """Generate CAN signals from the encoding."""
    signals = []
    dlc = 0

    mux_signals = [
        piece.extended_data.get("mux_signal")
        for piece in encoding
        if piece.extended_data.get("mux_signal")
    ]

    for piece in encoding:
        mux_count = piece.extended_data.get("mux_count")
        mux_ids = list(range(mux_count)) if mux_count is not None else []

        signals.append(
            CanSignal(
                name=piece.name.replace("::", "_"),
                start=(piece.bitstart + 7)
                if piece.endianess != "little"
                else piece.bitstart,
                type=piece.type,
                length=piece.bitlength,
                byte_order="big_endian"
                if piece.endianess == "big"
                else "little_endian",
                is_signed=is_signed(piece),
                is_multiplexer=piece.name in mux_signals,
                multiplexer_ids=mux_ids,
                multiplexer_signal=piece.extended_data.get("mux_signal"),
            )
        )

        dlc = max(dlc, ceil((piece.bitstart + piece.bitlength) / 8))

    return signals, dlc


def map_messages_to_device(msgs: List[CanMessage]) -> Dict[str, List[CanMessage]]:
    """Map CAN messages to their corresponding devices."""
    dev_messages = {}

    for msg in msgs:
        for sender in msg.senders:
            dev_messages.setdefault(sender, []).append(msg)

    return dev_messages


def init_can_data(fcp: FcpV2) -> Tuple[List[CanMessage], List[CanNode]]:
    """Initialize CAN messages and devices from the FCP."""
    messages = []
    devices = []
    encoder = make_encoder("packed", fcp)

    for extension in fcp.get_matching_extensions("can"):
        encoding = encoder.generate(extension)
        signals, dlc = make_signals(encoding)

        frame_id = extension.fields.get("id")
        if frame_id is None:
            return Err("No id field found in extension").unwrap()

        device_name = extension.fields.get("device", "Global")

        if not any(node.name == device_name for node in devices):
            devices.append(CanNode(device_name))

        messages.append(
            CanMessage(
                frame_id=frame_id,
                name=extension.name,
                length=dlc,
                signals=signals,
                senders=[device_name],
            )
        )

    return messages, devices


class CanCWritter:
    def __init__(self, fcp: FcpV2) -> None:
        """Initialize CanCWritter with FCP and output directory."""
        self.messages, self.devices = init_can_data(fcp)
        self.env = Environment(loader=FileSystemLoader("plugins/fcp_can_c/templates"))

        self.templates = {
            "device_can_h": self.env.get_template("can_device_h.jinja"),
            "device_can_c": self.env.get_template("can_device_c.jinja"),
        }
        self.dev_messages = map_messages_to_device(self.messages)

    def gen_static_files(self) -> Generator[Tuple[str, str], None, None]:
        """Generate all static fcp_can C files"""

        with open("plugins/fcp_can_c/templates/can_frame.h", "r") as f:
            yield "can_frame.h", f.read()

        with open("plugins/fcp_can_c/templates/can_signal_parser.h", "r") as f:
            yield "can_signal_parser.h", f.read()

        with open("plugins/fcp_can_c/templates/can_signal_parser.c", "r") as f:
            yield "can_signal_parser.c", f.read()

    def gen_device_headers(self) -> Generator[Tuple[str, str], None, None]:
        """Generate a C header file for each device."""

        for dev_name, msgs in self.dev_messages.items():
            yield (
                dev_name,
                self.templates["device_can_h"].render(
                    {
                        "dev_name": dev_name,
                        "messages": msgs,
                    }
                ),
            )

    def gen_device_source(self, device: str) -> str:
        """Generate a C source file for the given device."""
        raise NotImplementedError
