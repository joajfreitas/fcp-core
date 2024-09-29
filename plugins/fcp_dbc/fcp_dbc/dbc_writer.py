from beartype.typing import Any, List, Dict, NoReturn
from math import log2, ceil

from cantools.database.can.database import Database as CanDatabase
from cantools.database.can.message import Message as CanMessage
from cantools.database.can.signal import Signal as CanSignal

from fcp.specs import Signal, Enum, Struct, Extension, SignalBlock
from fcp import FcpV2

from fcp.maybe import Some, maybe
from fcp.result import Result
from fcp.maybe import catch


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

    def get_default_types(self) -> List[str]:
        return [
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

    def get_bitlength(self, signal: Signal) -> int:
        default_types = self.get_default_types()

        if signal.type in default_types:
            return int(signal.type[1:])

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
        mux_signals: List[str],
        prefix: str = "",
    ) -> NoReturn:
        self.signals.append(
            CanSignal(
                prefix + signal.name,
                self.get_bitstart(signal, extension)
                + (7 if self.get_field("endianness", extension) == "big" else 0),
                ceil(log2(len(enum.unwrap().enumeration))),
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
        )

    def convert_default_signal(
        self,
        signal: Signal,
        extension: Extension,
        signal_block: SignalBlock,
        mux_signals: List[str],
        prefix: str = "",
    ) -> NoReturn:
        self.signals.append(
            CanSignal(
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
        )

    def convert_signal(
        self,
        signal: Signal,
        extension: Extension,
        signal_block: SignalBlock,
        mux_signals: List[str],
        prefix: str = "",
    ) -> NoReturn:
        if signal.type in self.get_default_types():
            self.convert_default_signal(
                signal, extension, signal_block, mux_signals, prefix=prefix
            )
            return

        type = self.fcp.get_type(signal.type)
        if type.is_some() and isinstance(type.unwrap(), Enum):
            self.convert_enum(signal, type, extension, mux_signals)
            return
        elif type.is_some() and isinstance(type.unwrap(), Struct):
            self.convert_struct(
                signal, type.unwrap(), extension, signal_block, mux_signals, prefix
            )
            return

        raise KeyError()

    def convert(self, struct: Struct, extension: Extension) -> NoReturn:
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

    def get_dlc(self) -> int:
        return ceil(self.bitstart / 8)


@catch  # type: ignore
def write_dbc(fcp: FcpV2) -> Result[str, str]:
    messages = []

    for extension in fcp.get_matching_extensions("can"):
        struct = fcp.get_struct(extension.type).attempt()

        message_codec = MessageCodec(fcp)
        message_codec.convert(struct, extension)

        messages.append(
            CanMessage(
                frame_id=extension.fields.get("id"),
                name=struct.name,
                length=message_codec.get_dlc(),
                signals=message_codec.signals,
                senders=[],
            )
        )

    db = CanDatabase(messages=messages, nodes=[])

    return Some(str(db.as_dbc_string(sort_signals="default")))
