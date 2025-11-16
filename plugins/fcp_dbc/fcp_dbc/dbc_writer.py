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


"""Dbc writer."""

from beartype.typing import Tuple, List, Dict, Any
from math import ceil
from collections import defaultdict

from cantools.database.can.database import Database as CanDatabase
from cantools.database.can.message import Message as CanMessage
from cantools.database.can.signal import Signal as CanSignal
from cantools.database.can.node import Node as CanNode

from fcp.specs.v2 import FcpV2
from fcp.result import Result, Ok, Err
from fcp.maybe import catch
from fcp.encoding import make_encoder, EncodeablePiece, PackedEncoderContext


def extract_signals(
    piece: EncodeablePiece, prefix: str = ""
) -> List[Tuple[str, EncodeablePiece]]:
    """Flatten nested structs and arrays into individual signals."""
    signals: List[Tuple[str, EncodeablePiece]] = []
    base_prefix = f"{prefix}{piece.name}"
    nested = getattr(piece, "nested_fields", None)
    array_count = piece.extended_data.get("array_length")

    if array_count:
        for i in range(array_count):
            indexed_prefix = f"{base_prefix}_{i}_"
            if nested:
                for sub in nested:
                    signals.extend(extract_signals(sub, indexed_prefix))
            else:
                signals.append((indexed_prefix[:-1], piece))
        return signals

    if nested:
        new_prefix = f"{base_prefix}_"
        for sub in nested:
            if hasattr(sub, "nested_fields") and sub.nested_fields:
                signals.extend(extract_signals(sub, new_prefix))
            else:
                signals.append((f"{new_prefix}{sub.name}", sub))
    else:
        signals.append((base_prefix, piece))

    return signals


def _make_signals(
    encoding: List[EncodeablePiece], type: str
) -> Tuple[List[CanSignal], int]:
    signals: List[CanSignal] = []
    dlc = 0
    msg_bitlength = encoding[-1].bitstart + encoding[-1].bitlength
    if msg_bitlength > 64:
        raise ValueError(f"Message {type} too big. Current length: {msg_bitlength}")

    flat_signals: List[Tuple[str, EncodeablePiece]] = []
    for piece in encoding:
        flat_signals.extend(extract_signals(piece))

    mux_signal_names = set()
    for sig_name, leaf in flat_signals:
        m = leaf.extended_data.get("mux_signal")
        if m is not None:
            mux_signal_names.add(m)

    for sig_name, leaf in flat_signals:
        mux_count = leaf.extended_data.get("mux_count")
        mux_ids = list(range(0, mux_count)) if mux_count is not None else None
        is_signed_value = (
            leaf.type.is_signed() if hasattr(leaf.type, "is_signed") else False
        )
        is_multiplexer_flag = (
            leaf.extended_data.get("is_multiplexer") is True
            or sig_name in mux_signal_names
            or leaf.name in mux_signal_names
        )

        signals.append(
            CanSignal(
                sig_name.replace("::", "_"),
                (leaf.bitstart + 7) if leaf.endianess != "little" else leaf.bitstart,
                leaf.bitlength,
                byte_order=(
                    "big_endian" if leaf.endianess == "big" else "little_endian"
                ),
                is_signed=is_signed_value,
                minimum=0,
                maximum=0,
                unit=leaf.unit,
                comment=None,
                is_multiplexer=is_multiplexer_flag,
                multiplexer_ids=mux_ids,
                multiplexer_signal=leaf.extended_data.get("mux_signal"),
            )
        )

        dlc = max(dlc, ceil((leaf.bitstart + leaf.bitlength) / 8))

    return signals, dlc


@catch  # type: ignore
def write_dbc(fcp: FcpV2) -> Result[str, str]:
    """Write dbc."""
    buses: Dict[str, Any] = defaultdict(lambda: {"messages": list(), "nodes": list()})

    encoder = make_encoder(
        "packed", fcp, PackedEncoderContext().with_unroll_arrays(True)
    )

    for impl in fcp.get_matching_impls("can"):
        bus = impl.get_field("bus", "default").unwrap()

        encoding = encoder.generate(impl)

        signals, dlc = _make_signals(encoding, impl.type)

        id = impl.fields.get("id")
        if id is None:
            return Err("No id field found in extension")

        buses[bus]["messages"].append(
            CanMessage(
                frame_id=id,
                name=impl.name,
                length=dlc,
                signals=list(reversed(signals)),
                senders=[],
            )
        )
        device = impl.fields.get("device")
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
