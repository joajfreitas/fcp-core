from pathlib import Path
from beartype.typing import Tuple, List, Dict, Any, Union, NoReturn, Optional
from math import ceil

from cantools.database.can.database import Database as CanDatabase
from cantools.database.can.message import Message as CanMessage
from cantools.database.can.node import Node as CanNode

from fcp.specs import Signal
from fcp import FcpV2

from dataclasses import dataclass
from fcp.result import Result, Ok, Err
from fcp.maybe import catch
from fcp.encoding import make_encoder, EncodeablePiece, Value


@dataclass
class CanSignal:
    name: str
    start: int
    type: str
    length: int
    is_signed: bool
    type: str
    byte_order: str
    minimum: Optional[str]
    maximum: Optional[str]
    unit: Optional[str]
    comment: Optional[str]
    is_multiplexer: bool
    multiplexer_ids: List[int]
    multiplexer_signal: Optional[str]


def is_signed(value: Value) -> bool:
    return bool(value.type[0] == "i")


def make_signals(encoding: List[EncodeablePiece]) -> Tuple[List[Signal], int]:
    signals = []
    dlc = 0

    mux_signals = [
        piece.extended_data.get("mux_signal")
        for piece in encoding
        if piece.extended_data.get("mux_signal") is not None
    ]

    for piece in encoding:
        breakpoint()

        mux_count = piece.extended_data.get("mux_count")
        mux_ids = list(range(0, mux_count)) if mux_count is not None else []

        signals.append(
            CanSignal(
                name=piece.name.replace("::", "_"),
                start=(piece.bitstart + 7)
                if piece.endianess != "little"
                else piece.bitstart,
                type=piece.type,
                length=piece.bitlength,
                byte_order=(
                    "big_endian" if piece.endianess == "big" else "little_endian"
                ),
                is_signed=is_signed(piece),
                minimum=None,
                maximum=None,
                unit=None,
                comment=None,
                is_multiplexer=piece.name in mux_signals,
                multiplexer_ids=mux_ids,
                multiplexer_signal=piece.extended_data.get("mux_signal"),
            )
        )

        dlc = ceil((piece.bitstart + piece.bitlength) / 8)

    return signals, dlc


def init_can_data(fcp: FcpV2) -> Tuple[List[CanMessage], List[CanNode]]:
    messages = []
    devices = []
    encoder = make_encoder("packed", fcp)

    for extension in fcp.get_matching_extensions("can"):
        encoding = encoder.generate(extension)

        signals, dlc = make_signals(encoding)

        id = extension.fields.get("id")
        if id is None:
            return Err("No id field found in extension").unwrap()

        device = extension.fields.get("device")
        device_name = device if device is not None else "Global"

        if device_name not in devices:
            devices.append(CanNode(device_name))

        messages.append(
            CanMessage(
                frame_id=id,
                name=extension.name,
                length=dlc,
                signals=signals,
                senders=[device_name],
            )
        )

    return messages, devices


class CanCWritter:
    def __init__(self, fcp: FcpV2, output_dir: Path) -> None:
        self.messages, self.devices = init_can_data(fcp)
        self.output_dir = output_dir

    def get_device_dict(self, device: str) -> Dict[str, Any]:
        return {
            "device": device,
            "msgs": [msg for msg in self.messages if device in msg.senders],
        }

    def get_device_header(self, device: str) -> str:
        msgs = self.get_device_msgs(device)

        raise NotImplementedError

    def get_device_source(self, device: str) -> str:
        msgs = self.get_device_msgs(device)

        raise NotImplementedError
