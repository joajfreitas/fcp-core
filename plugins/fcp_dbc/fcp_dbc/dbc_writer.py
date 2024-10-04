from beartype.typing import Any, List, Dict, NoReturn
from math import log2, ceil

from cantools.database.can.database import Database as CanDatabase
from cantools.database.can.message import Message as CanMessage
from cantools.database.can.signal import Signal as CanSignal

from fcp.specs import Signal, Enum, Struct, Extension, SignalBlock
from fcp import FcpV2

from fcp.types import Nil
from fcp.maybe import Some, maybe
from fcp.result import Result, Err, Ok
from fcp.maybe import catch
from fcp.specs.type import Type
from fcp.encoding import make_encoder, EncodeablePiece


def is_signed(signal: Signal) -> bool:
    return bool(signal.type[0] == "i")


def is_multiplexer(signal: Signal, mux_signals: List[str]) -> bool:
    return signal.name in mux_signals


class MessageCodec:
    def __init__(self, fcp: FcpV2) -> None:
        self.signals: List[Signal] = []
        self.bitstart = 0
        self.fcp = fcp

    def get_fields(self, extension: Extension) -> Dict[str, Any]:
        return extension.fields

    def get_bitstart(self, signal: Signal, extension: Extension) -> int:
        fields = self.get_fields(extension)
        bitstart = maybe(fields.get("bitstart"))

        if bitstart.is_some():
            return int(bitstart.unwrap())
        else:
            bitstart = self.bitstart
            self.bitstart += self.get_bitlength(signal)
            return int(bitstart)

    def get_bitlength(self, signal: Signal) -> int:
        if signal.type in Type.get_default_types():
            return int(Type.make_type(signal.type).get_length())

        type = self.fcp.get_type(signal.type)
        if type.is_some() and isinstance(type.unwrap(), Enum):
            return ceil(log2(len(type.unwrap().enumeration)))
        else:
            raise ValueError("Can't deal with custom types")

    def get_field(self, name: str, extension: Extension) -> Any:
        default_fields = {
            "scale": 1.0,
            "offset": 0.0,
            "minimum": 0,
            "maximum": 0,
            "device": "",
            "endianness": "little",
            "mux_count": None,
        }

        fields = maybe(self.get_fields(extension))
        if fields.is_nothing():
            return default_fields.get(name)
        else:
            return fields.unwrap().get(name, default_fields.get(name))

    def convert_struct(
        self,
        signal: Signal,
        struct: Struct,
        extension: Extension,
        signal_block: SignalBlock,
        mux_signals: List[str],
        prefix: str = "",
    ) -> NoReturn:

        for s in struct.signals:
            self.convert_signal(
                s,
                extension,
                signal_block,
                mux_signals,
                prefix=prefix + signal.name + "_",
            )

    def convert_enum(
        self,
        signal: Signal,
        enum: Enum,
        extension: Extension,
        signal_block: SignalBlock,
        mux_signals: List[str],
        prefix: str = "",
    ) -> Signal:

        signal = self.convert_default_signal(
            signal, extension, signal_block, mux_signals, prefix
        )

        signal.length = ceil(log2(len(enum.enumeration)))

        return signal

    def convert_default_signal(
        self,
        signal: Signal,
        extension: Extension,
        signal_block: SignalBlock,
        mux_signals: List[str],
        prefix: str = "",
    ) -> NoReturn:
        return CanSignal(
            prefix + signal.name,
            self.get_bitstart(signal, extension)
            + (7 if self.get_field("endianness", extension) == "big" else 0),
            self.get_bitlength(signal),
            byte_order=(
                "big_endian"
                if self.get_field("endianness", extension) == "big"
                else "little_endian"
            ),
            is_signed=is_signed(signal),
            minimum=self.get_field("minimum", extension),
            maximum=self.get_field("maximum", extension),
            unit=signal.unit or None,
            comment=signal.comment or None,
            is_multiplexer=signal.name in mux_signals,
            multiplexer_ids=(
                list(range(mux_count))
                if (mux_count := self.get_field("mux_count", extension)) is not None
                else None
            ),
            multiplexer_signal=self.get_field("mux_signal", extension),
            receivers=[],
        )

    @catch  # type: ignore
    def convert_signal(
        self,
        signal: Signal,
        extension: Extension,
        signal_block: SignalBlock,
        mux_signals: List[str],
        prefix: str = "",
    ) -> Result[Nil, str]:
        if signal.type in Type.get_default_types():
            self.signals.append(
                self.convert_default_signal(
                    signal, extension, signal_block, mux_signals, prefix=prefix
                )
            )
            return Ok(())

        type = self.fcp.get_type(signal.type).attempt()
        if isinstance(type, Enum):
            self.signals.append(
                self.convert_enum(signal, type, extension, signal_block, mux_signals)
            )
            return
        elif isinstance(type, Struct):
            self.convert_struct(
                signal, type, extension, signal_block, mux_signals, prefix
            )
            return

        return Err("Can't deal with this")

    @catch  # type: ignore
    def convert(self, struct: Struct, extension: Extension) -> Result[Nil, str]:
        mux_signals = [
            extension.get_signal_fields(signal.name).and_then(
                lambda fields: fields.get("mux_signal")
            )
            for signal in struct.signals
        ]

        mux_signals = [x for x in mux_signals if x is not None]

        for signal in struct.signals:
            signal_block = extension.get_signal(signal.name)

            self.convert_signal(signal, extension, signal_block, mux_signals)

        return Ok(())

    def get_dlc(self) -> int:
        return ceil(self.bitstart / 8)


def make_signals(encoding: List[EncodeablePiece]) -> List[Signal]:
    signals = []

    mux_signals = [
        piece.mux_signal for piece in encoding if piece.mux_signal is not None
    ]

    for piece in encoding:
        if piece.mux_count is not None:
            mux_ids = list(range(0, piece.mux_count))
        else:
            mux_ids = None

        signals.append(
            CanSignal(
                piece.name.replace("::", "_"),
                (piece.bitstart + 7) if piece.endianess != "little" else piece.bitstart,
                piece.bitlength,
                byte_order=(
                    "big_endian" if piece.endianess == "big" else "little_endian"
                ),
                is_signed=False,
                minimum=0,
                maximum=0,
                unit=None,
                comment=None,
                is_multiplexer=piece.name in mux_signals,
                multiplexer_ids=mux_ids,
                multiplexer_signal=piece.mux_signal,
            )
        )

    dlc = ceil((piece.bitstart + piece.bitlength) / 8)

    return signals, dlc


@catch  # type: ignore
def write_dbc(fcp: FcpV2) -> Result[str, str]:
    messages = []

    encoder = make_encoder("packed", fcp)

    for extension in fcp.get_matching_extensions("can"):
        encoding = encoder.generate(extension)

        signals, dlc = make_signals(encoding)

        messages.append(
            CanMessage(
                frame_id=extension.fields.get("id"),
                name=extension.name,
                length=dlc,
                signals=signals,
                senders=[],
            )
        )

    db = CanDatabase(messages=messages, nodes=[])

    return Some(str(db.as_dbc_string(sort_signals="default")))
