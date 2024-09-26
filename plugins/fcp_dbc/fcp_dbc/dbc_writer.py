from beartype.typing import Any, List

from cantools.database.can.database import Database as CanDatabase
from cantools.database.can.message import Message as CanMessage
from cantools.database.can.signal import Signal as CanSignal

from fcp.specs import Signal, SignalBlock
from fcp import FcpV2


def is_signed(signal: Signal) -> bool:
    return bool(signal.type[0] == "i")


def is_multiplexer(signal: Signal, mux_signals: List[str]) -> bool:
    return signal.name in mux_signals


class SignalCodec:
    def __init__(self) -> None:
        self.bitstart = 0

    def get_fields(self) -> Any:
        return self.ext.fields if self.ext else {}

    def get_bitstart(self) -> int:
        if self.ext is not None and self.ext.fields.get("bitstart"):
            return int(self.ext.fields.get("bitstart"))
        else:
            bitstart = self.bitstart
            self.bitstart += self.get_bitlength()
            return int(bitstart)

    def get_bitlength(self) -> int:
        default_types = [
            "u8",
            "u16",
            "u32",
            "u64",
            "i8",
            "i16",
            "i32",
            "i64",
            "f32",
            "f64",
        ]

        if self.signal.type in default_types:
            return int(self.signal.type[1:])
        else:
            raise ValueError("Can't deal with custom types")

    def get_field(self, name: str) -> Any:
        fields = {
            "scale": 1.0,
            "offset": 0.0,
            "minimum": 0,
            "maximum": 0,
            "device": "",
            "endianness": "little",
            "mux_count": None,
        }

        return self.get_fields().get(name, fields.get(name))

    def convert(
        self, signal: Signal, extension: SignalBlock, mux_signals: List[str]
    ) -> CanSignal:
        self.signal = signal
        self.ext = extension

        return CanSignal(
            self.signal.name,
            self.get_bitstart() + (7 if self.get_field("endianness") == "big" else 0),
            self.get_bitlength(),
            byte_order=(
                "big_endian"
                if self.get_field("endianness") == "big"
                else "little_endian"
            ),
            is_signed=is_signed(self.signal),
            minimum=self.get_field("minimum"),
            maximum=self.get_field("maximum"),
            unit=self.signal.unit or None,
            comment=self.signal.comment or None,
            is_multiplexer=signal.name in mux_signals,
            multiplexer_ids=(
                list(range(mux_count))
                if (mux_count := self.get_field("mux_count")) is not None
                else None
            ),
            multiplexer_signal=self.get_field("mux_signal"),
            receivers=[],
        )


def write_dbc(fcp: FcpV2) -> str:
    messages = []

    for struct in fcp.structs:
        extension = fcp.get_matching_extension(struct, "can")

        mux_signals = [
            extension.get_signal_fields(signal.name).get("mux_signal")
            for signal in struct.signals
        ]

        mux_signals = [x for x in mux_signals if x is not None]

        signal_codec = SignalCodec()
        signals = [
            signal_codec.convert(signal, extension.get_signal(signal.name), mux_signals)
            for signal in struct.signals
        ]

        messages.append(
            CanMessage(
                frame_id=extension.fields.get("id"),
                name=struct.name,
                length=8,
                signals=signals,
                senders=[],
            )
        )

    db = CanDatabase(messages=messages, nodes=[])

    return str(db.as_dbc_string(sort_signals="default"))
