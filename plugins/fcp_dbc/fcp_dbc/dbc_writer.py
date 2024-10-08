from beartype.typing import Tuple, List
from math import ceil

from cantools.database.can.database import Database as CanDatabase
from cantools.database.can.message import Message as CanMessage
from cantools.database.can.signal import Signal as CanSignal
from cantools.database.can.node import Node as CanNode

from fcp import FcpV2

from fcp.result import Result, Ok, Err
from fcp.maybe import catch
from fcp.encoding import make_encoder, EncodeablePiece, Value


def is_signed(value: Value) -> bool:
    return bool(value.type[0] == "i")


def make_signals(encoding: List[EncodeablePiece]) -> Tuple[List[CanSignal], int]:
    signals = []
    dlc = 0

    mux_signals = [
        piece.extended_data.get("mux_signal")
        for piece in encoding
        if piece.extended_data.get("mux_signal") is not None
    ]

    for piece in encoding:
        mux_count = piece.extended_data.get("mux_count")
        mux_ids = list(range(0, mux_count)) if mux_count is not None else None

        signals.append(
            CanSignal(
                piece.name.replace("::", "_"),
                (piece.bitstart + 7) if piece.endianess != "little" else piece.bitstart,
                piece.bitlength,
                byte_order=(
                    "big_endian" if piece.endianess == "big" else "little_endian"
                ),
                is_signed=is_signed(piece),
                minimum=0,
                maximum=0,
                unit=piece.unit,
                comment=None,
                is_multiplexer=piece.name in mux_signals,
                multiplexer_ids=mux_ids,
                multiplexer_signal=piece.extended_data.get("mux_signal"),
            )
        )

        dlc = ceil((piece.bitstart + piece.bitlength) / 8)

    return signals, dlc


@catch  # type: ignore
def write_dbc(fcp: FcpV2) -> Result[str, str]:
    messages = []
    nodes = []

    encoder = make_encoder("packed", fcp)

    for extension in fcp.get_matching_impls("can"):
        encoding = encoder.generate(extension)

        signals, dlc = make_signals(encoding)

        id = extension.fields.get("id")
        if id is None:
            return Err("No id field found in extension")

        messages.append(
            CanMessage(
                frame_id=id,
                name=extension.name,
                length=dlc,
                signals=signals,
                senders=[],
            )
        )
        device = extension.fields.get("device")
        if device is not None and device not in nodes:
            nodes.append(device)

    db = CanDatabase(messages=messages, nodes=[CanNode(name=node) for node in nodes])

    return Ok(str(db.as_dbc_string(sort_signals="default")))
