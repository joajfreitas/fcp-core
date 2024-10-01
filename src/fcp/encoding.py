from beartype.typing import Union, NoReturn, List

from .specs.struct import Struct
from .specs.enum import Enum
from .specs.signal import Signal
from .specs.type import Type
from .specs.v2 import FcpV2


class Value:
    def __init__(self, name: str, bitstart: int, bitlength: int) -> None:
        self.name = name
        self.bitstart = bitstart
        self.bitlength = bitlength

    def __repr__(self) -> str:
        return f"Value name={self.name} bitstart={self.bitstart} bitlength={self.bitlength}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Value):
            return NotImplemented

        return (
            self.name == other.name
            and self.bitstart == other.bitstart
            and self.bitlength == other.bitlength
        )


EncodablePiece = Union[Value]


class PackedEncoding:
    def __init__(self, fcp: FcpV2):
        self.fcp = fcp
        self.encoding: List[Value] = []
        self.bitstart = 0

    def generate_struct(self, struct: Struct, prefix: str = "") -> NoReturn:
        for signal in sorted(struct.signals, key=lambda signal: signal.field_id):
            self.generate_signal(signal, prefix)

    def generate_signal(self, signal: Signal, prefix: str = "") -> NoReturn:
        if signal.type not in Type.get_default_types():
            self._generate(
                self.fcp.get_type(signal.type).unwrap(), prefix=signal.type + "::"
            )
            return

        type_length = Type.make_type(signal.type).get_length()
        self.encoding.append(Value(prefix + signal.name, self.bitstart, type_length))

        self.bitstart += type_length

    def generate_enum(self, enum: Enum) -> NoReturn:
        pass

    def _generate(
        self, type: Union[Struct, Enum, Signal], prefix: str = ""
    ) -> NoReturn:
        if isinstance(type, Struct):
            self.generate_struct(type, prefix)
        elif isinstance(type, Signal):
            self.generate_signal(type, prefix)
        else:
            raise KeyError(f"Invalid type {type}")

    def generate(self, type: Union[Struct, Enum, Signal]) -> List[EncodablePiece]:
        self.encoding = []
        self.bitstart = 0

        self._generate(type)
        return self.encoding


def make_encoding(name: str, fcp: FcpV2) -> Union[PackedEncoding]:
    if name == "packed":
        return PackedEncoding(fcp)

    raise KeyError(f"Invalid encoding name {name}")
