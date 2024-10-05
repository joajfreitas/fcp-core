from beartype.typing import Union, NoReturn, List, Dict, Any
from math import log2, ceil

from .specs.struct import Struct
from .specs.enum import Enum
from .specs.signal import Signal
from .specs.type import Type
from .specs.v2 import FcpV2
from .specs.impl import Impl
from .maybe import Some


class Value:
    def __init__(
        self,
        name: str,
        type: str,
        bitstart: int,
        bitlength: int,
        endianess: str = "little",
        extended_data: Dict[str, Any] = dict(),
    ) -> None:
        self.name = name
        self.type = type
        self.bitstart = bitstart
        self.bitlength = bitlength
        self.endianess = endianess
        self.extended_data = extended_data

    def __repr__(self) -> str:
        return f"Value name={self.name} type={self.type} bitstart={self.bitstart} bitlength={self.bitlength} endianess={self.endianess}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Value):
            return NotImplemented

        return (
            self.name == other.name
            and self.type == other.type
            and self.bitstart == other.bitstart
            and self.bitlength == other.bitlength
            and self.endianess == other.endianess
        )


EncodeablePiece = Union[Value]


class PackedEncoder:
    def __init__(self, fcp: FcpV2):
        self.fcp = fcp
        self.encoding: List[Value] = []
        self.bitstart = 0

    def generate_struct(
        self, struct: Struct, extension: Impl, prefix: str = ""
    ) -> NoReturn:
        for signal in sorted(struct.signals, key=lambda signal: signal.field_id):
            self.generate_signal(signal, extension, prefix)

    def generate_signal(
        self, signal: Signal, extension: Impl, prefix: str = ""
    ) -> NoReturn:

        fields: Dict[str, Any] = (
            extension.get_signal(signal.name)
            .and_then(lambda signal_block: Some(signal_block.fields))
            .unwrap_or({})
        )

        if signal.type not in Type.get_default_types():
            self._generate(
                self.fcp.get_type(signal.type).unwrap(),
                extension,
                prefix=prefix + signal.name + "::",
            )
            return

        type_length = Type.make_type(signal.type).get_length()

        self.encoding.append(
            Value(
                prefix + signal.name,
                signal.type,
                self.bitstart,
                type_length,
                endianess=fields.get("endianess") or "little",
                extended_data=fields,
            )
        )

        self.bitstart += type_length

    def generate_enum(self, enum: Enum, extension: Impl, prefix: str) -> NoReturn:
        type_length = ceil(
            log2(max([enumeration.value for enumeration in enum.enumeration]) + 1)
        )

        if type_length > 64:
            raise ValueError(f"Way too large an enum, computed size: {type_length}")

        self.encoding.append(
            Value(prefix[:-2], "u" + str(type_length), self.bitstart, type_length)
        )
        self.bitstart += type_length

    def _generate(
        self, type: Union[Struct, Enum, Signal], extension: Impl, prefix: str = ""
    ) -> NoReturn:
        if isinstance(type, Struct):
            self.generate_struct(type, extension, prefix)
        elif isinstance(type, Signal):
            self.generate_signal(type, extension, prefix)
        elif isinstance(type, Enum):
            self.generate_enum(type, extension, prefix)
        else:
            raise KeyError(f"Invalid type {type}")

    def generate(self, extension: Impl) -> List[EncodeablePiece]:
        self.encoding = []
        self.bitstart = 0

        self._generate(self.fcp.get_type(extension.type).unwrap(), extension)
        return self.encoding


def make_encoder(name: str, fcp: FcpV2) -> Union[PackedEncoder]:
    if name == "packed":
        return PackedEncoder(fcp)

    raise KeyError(f"Invalid encoding name {name}")
