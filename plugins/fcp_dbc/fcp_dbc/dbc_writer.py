"""Dbc writer."""

"""Copyright (c) 2024 the fcp AUTHORS.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from beartype.typing import Tuple, List, Dict, Any
from math import ceil
from collections import defaultdict

from cantools.database.can.database import Database as CanDatabase
from cantools.database.can.message import Message as CanMessage
from cantools.database.can.signal import Signal as CanSignal
from cantools.database.can.node import Node as CanNode

from fcp import FcpV2

from fcp.result import Result, Ok, Err
from fcp.maybe import catch
from fcp.encoding import make_encoder, EncodeablePiece


def _make_signals(
    encoding: List[EncodeablePiece], type: str
) -> Tuple[List[CanSignal], int]:
    signals = []
    dlc = 0

    mux_signals = [
        piece.extended_data.get("mux_signal")
        for piece in encoding
        if piece.extended_data.get("mux_signal") is not None
    ]

    msg_bitlength = encoding[-1].bitstart + encoding[-1].bitlength
    if msg_bitlength > 64:
        raise ValueError(f"Message {type} too big. Current length: {msg_bitlength}")

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
                is_signed=piece.type.is_signed(),
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
    """Write dbc."""
    buses: Dict[str, Any] = defaultdict(lambda: {"messages": list(), "nodes": list()})

    encoder = make_encoder("packed", fcp)

    for extension in fcp.get_matching_impls("can"):
        bus = extension.get_field("bus", "default").unwrap()

        encoding = encoder.generate(extension)

        signals, dlc = _make_signals(encoding, extension.type)

        id = extension.fields.get("id")
        if id is None:
            return Err("No id field found in extension")

        buses[bus]["messages"].append(
            CanMessage(
                frame_id=id,
                name=extension.name,
                length=dlc,
                signals=signals,
                senders=[],
            )
        )
        device = extension.fields.get("device")
        if device is not None and device not in buses[bus]["nodes"]:
            buses[bus]["nodes"].append(device)

    dbs = [
        (
            bus,
            CanDatabase(
                messages=buses[bus]["messages"],
                nodes=[CanNode(name=node) for node in buses[bus]["nodes"]],
            ),
        )
        for bus in buses
    ]

    return Ok([(bus, str(db.as_dbc_string(sort_signals="default"))) for bus, db in dbs])
