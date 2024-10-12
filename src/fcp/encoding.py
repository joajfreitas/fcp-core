from beartype.typing import Union, NoReturn, List, Dict, Any, Optional
from math import log2, ceil
from copy import copy

from .specs.struct import Struct
from .specs.enum import Enum
from .specs.struct_field import StructField
from .specs.type import Type, CompoundType, DefaultType, ArrayType
from .specs.v2 import FcpV2
from .specs.impl import Impl
from .maybe import Some


def derive_scalar_from_array(type: ArrayType) -> Type:
    return type.type


class Value:
    def __init__(
        self,
        name: str,
        type: Type,
        bitstart: int,
        bitlength: int,
        endianess: str = "little",
        unit: Optional[str] = None,
        extended_data: Dict[str, Any] = dict(),
    ) -> None:
        self.name = name
        self.type = type
        self.bitstart = bitstart
        self.bitlength = bitlength
        self.endianess = endianess
        self.extended_data = extended_data
        self.unit = unit

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
        for field in sorted(struct.fields, key=lambda field: field.field_id):
            self.generate_signal(field, extension, prefix)

    def generate_signal(
        self, field: StructField, extension: Impl, prefix: str = ""
    ) -> NoReturn:

        fields: Dict[str, Any] = (
            extension.get_signal(field.name)
            .and_then(lambda signal_block: Some(signal_block.fields))
            .unwrap_or({})
        )

        if isinstance(field.type, CompoundType):
            self._generate(
                field.type,
                extension,
                prefix=prefix + field.name + "::",
            )
            return
        elif isinstance(field.type, ArrayType):
            self.generate_array_type(field.type, field, extension, prefix)
            return

        type_length = field.type.get_length()

        self.encoding.append(
            Value(
                prefix + field.name,
                field.type,
                self.bitstart,
                type_length,
                endianess=fields.get("endianess") or "little",
                extended_data=fields,
                unit=field.unit,
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
            Value(
                prefix[:-2],
                DefaultType("u" + str(type_length)),  # type: ignore
                self.bitstart,
                type_length,
            )
        )
        self.bitstart += type_length

    def generate_compound_type(
        self, type: CompoundType, extension: Impl, prefix: str = ""
    ) -> NoReturn:
        type = self.fcp.get_type(type).unwrap()
        if isinstance(type, Struct):
            self.generate_struct(type, extension, prefix)
        elif isinstance(type, StructField):
            self.generate_signal(type, extension, prefix)
        elif isinstance(type, Enum):
            self.generate_enum(type, extension, prefix)
        else:
            raise KeyError(f"Invalid type {type}")

    def generate_array_type(
        self, type: ArrayType, field: StructField, extension: Impl, prefix: str = ""
    ) -> NoReturn:
        for i in range(type.size):
            derived_field = copy(field)

            derived_field.type = type.type
            derived_field.name = field.name + "_" + str(i)
            self.generate_signal(derived_field, extension, prefix)

    def _generate(self, type: Type, extension: Impl, prefix: str = "") -> NoReturn:
        self.generate_compound_type(type, extension, prefix)

    def generate(self, extension: Impl) -> List[EncodeablePiece]:
        self.encoding = []
        self.bitstart = 0

        self._generate(
            CompoundType(extension.type),  # type: ignore
            extension,
        )
        return self.encoding


def make_encoder(name: str, fcp: FcpV2) -> Union[PackedEncoder]:
    if name == "packed":
        return PackedEncoder(fcp)

    raise KeyError(f"Invalid encoding name {name}")
