<<<<<<< HEAD
"""Encoding."""

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


from beartype.typing import Union, NoReturn, List, Dict, Any, Optional
=======
from beartype.typing import Optional, Union, NoReturn, List, Dict, Any
>>>>>>> 156e3ae (Enum support for CAN C gen)
from math import log2, ceil
from copy import copy

from .specs.struct import Struct
from .specs.enum import Enum
from .specs.struct_field import StructField
from .specs.type import Type, ComposedType, BuiltinType, ArrayType
from .specs.v2 import FcpV2
from .specs.impl import Impl
from .maybe import Some


class Value:
    """Encodable piece value."""

    def __init__(
        self,
        name: str,
<<<<<<< HEAD
        type: Type,
=======
        type: str,  # scalar type (e.g. u8, i12, etc.)
>>>>>>> 156e3ae (Enum support for CAN C gen)
        bitstart: int,
        bitlength: int,
        endianess: str = "little",
        unit: Optional[str] = None,
        extended_data: Dict[str, Any] = dict(),
        composite_type: Optional[
            str
        ] = None,  # name of composit type (used for enums, structs...)
    ) -> None:
        self.name = name
        self.type = type
        self.bitstart = bitstart
        self.bitlength = bitlength
        self.endianess = endianess
        self.extended_data = extended_data
<<<<<<< HEAD
        self.unit = unit
=======
        self.composite_type = composite_type
>>>>>>> 156e3ae (Enum support for CAN C gen)

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
    """Packed encoder. Packs all bits really tight."""

    def __init__(self, fcp: FcpV2):
        self.fcp = fcp
        self.encoding: List[Value] = []
        self.bitstart = 0

    def _generate_struct(
        self, struct: Struct, extension: Impl, prefix: str = ""
    ) -> NoReturn:
        for field in sorted(struct.fields, key=lambda field: field.field_id):
            self._generate_signal(field, extension, prefix)

    def _generate_signal(
        self, field: StructField, extension: Impl, prefix: str = ""
    ) -> NoReturn:
        fields: Dict[str, Any] = (
            extension.get_signal(field.name)
            .and_then(lambda signal_block: Some(signal_block.fields))
            .unwrap_or({})
        )

        if isinstance(field.type, ComposedType):
            self._generate(
                field.type,
                extension,
                prefix=prefix + field.name + "::",
            )
            return
        elif isinstance(field.type, ArrayType):
            self._generate_array_type(field.type, field, extension, prefix)
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

    def _generate_enum(self, enum: Enum, extension: Impl, prefix: str) -> NoReturn:
        type_length = ceil(
            log2(max([enumeration.value for enumeration in enum.enumeration]) + 1)
        )

        if type_length > 64:
            raise ValueError(f"Way too large an enum, computed size: {type_length}")

        self.encoding.append(
            Value(
                prefix[:-2],
<<<<<<< HEAD
                BuiltinType("u" + str(type_length)),  # type: ignore
                self.bitstart,
                type_length,
=======
                "u" + str(type_length),
                self.bitstart,
                type_length,
                composite_type=enum.name,
>>>>>>> 156e3ae (Enum support for CAN C gen)
            )
        )
        self.bitstart += type_length

    def _generate_compound_type(
        self, type: ComposedType, extension: Impl, prefix: str = ""
    ) -> NoReturn:
        type = self.fcp.get_type(type).unwrap()
        if isinstance(type, Struct):
            self._generate_struct(type, extension, prefix)
        elif isinstance(type, StructField):
            self._generate_signal(type, extension, prefix)
        elif isinstance(type, Enum):
            self._generate_enum(type, extension, prefix)
        else:
            raise KeyError(f"Invalid type {type}")

    def _generate_array_type(
        self, type: ArrayType, field: StructField, extension: Impl, prefix: str = ""
    ) -> NoReturn:
        for i in range(type.size):
            derived_field = copy(field)

            derived_field.type = type.type
            derived_field.name = field.name + "_" + str(i)
            self._generate_signal(derived_field, extension, prefix)

    def _generate(self, type: Type, extension: Impl, prefix: str = "") -> NoReturn:
        self._generate_compound_type(type, extension, prefix)

    def generate(self, extension: Impl) -> List[EncodeablePiece]:
        """Generate encoding."""
        self.encoding = []
        self.bitstart = 0

        self._generate(
            ComposedType(extension.type),  # type: ignore
            extension,
        )
        return self.encoding


def make_encoder(name: str, fcp: FcpV2) -> Union[PackedEncoder]:
    """Create encoder from encoder name."""
    if name == "packed":
        return PackedEncoder(fcp)

    raise KeyError(f"Invalid encoding name {name}")
