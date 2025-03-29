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

"""Produce encodable instructions from an Fcp v2 AST.

Available encoders:
    * PackedEncoder - encoder for static length packed data

The generate function in the encoder returns a list of encodeable pieces.
Availble encodeable pieces:
    * Value - Value containing data in the payload

Usage example:

.. code-block: python

    encoder = make_encoder("packed", fcp, PackedEncoderContext())
    for impl in fcp.get_matching_impls("can"):
        for encodeable_piece in encoder.generate(impl):
            # encode it somehow
            ...
"""

from beartype.typing import Union, NoReturn, List, Dict, Any, Optional
from typing_extensions import Self, TypeAlias
from math import log2, ceil
from copy import copy

from .specs.struct import Struct
from .specs.enum import Enum
from .specs.struct_field import StructField
from .specs.type import (
    Type,
    BuiltinType,
    ArrayType,
    StructType,
    EnumType,
    UnsignedType,
    SignedType,
    FloatType,
    DoubleType,
)
from .specs.v2 import FcpV2
from .specs.impl import Impl
from .maybe import Some, Nothing


class Value:
    """Encodable piece data value."""

    def __init__(
        self,
        name: str,
        type: Type,
        bitstart: int,
        bitlength: int,
        endianess: str = "little",
        unit: Optional[str] = None,
        extended_data: Dict[str, Any] = dict(),
        composite_type: Optional[
            str
        ] = Nothing(),  # name of composit type (used for enums, structs...)
    ) -> None:
        self.name = name
        self.type = type
        self.bitstart = bitstart
        self.bitlength = bitlength
        self.endianess = endianess
        self.extended_data = extended_data
        self.unit = unit
        self.composite_type = composite_type

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


EncodeablePiece: TypeAlias = Union[Value]


class PackedEncoderContext:
    """Configuration options for the packed encoder."""

    def __init__(self, unroll_arrays: bool = False):
        self.unroll_arrays = unroll_arrays

    def with_unroll_arrays(self, unroll_arrays: bool) -> Self:
        """Unroll arrays into N scalar values."""
        this = copy(self)
        this.unroll_arrays = unroll_arrays
        return this


EncoderContext: TypeAlias = Union[PackedEncoderContext]


class PackedEncoder:
    """Packed encoder. Packs all bits really tight. Only handles static length data."""

    def __init__(self, fcp: FcpV2, ctx: PackedEncoderContext):
        self.fcp = fcp
        self.ctx = ctx
        self.encoding: List[Value] = []
        self.bitstart = 0

    def _get_type_length(self, fcp: FcpV2, type: Type) -> int:
        if isinstance(type, BuiltinType):
            return type.get_length()
        elif (
            isinstance(type, UnsignedType)
            or isinstance(type, SignedType)
            or isinstance(type, FloatType)
            or isinstance(type, DoubleType)
        ):
            return type.get_length()
        elif isinstance(type, ArrayType):
            return int(type.size * self._get_type_length(fcp, type.underlying_type))
        elif isinstance(type, EnumType):
            return int(
                2 ** ceil(log2(fcp.get_enum(type.name).unwrap().get_packed_size()))
            )
        else:
            raise ValueError("Error computing type length for type " + str(type))

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

        if isinstance(field.type, StructType):
            self._generate(
                field.type,
                extension,
                prefix=prefix + field.name + "::",
            )
            return
        elif isinstance(field.type, ArrayType) and self.ctx.unroll_arrays:
            self._generate_array_type(field.type, field, extension, prefix)
            return

        type_length = self._get_type_length(self.fcp, field.type)

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

    def _generate_enum(
        self, type: EnumType, enum: Enum, extension: Impl, prefix: str
    ) -> NoReturn:
        type_length = ceil(
            log2(max([enumeration.value for enumeration in enum.enumeration]) + 1)
        )

        if type_length > 64:
            raise ValueError(f"Way too large an enum, computed size: {type_length}")

        self.encoding.append(
            Value(
                prefix[:-2],
                type,
                self.bitstart,
                type_length,
                composite_type=Some(enum.name),
            )
        )
        self.bitstart += type_length

    def _generate_compound_type(
        self, type: Union[StructType, EnumType], extension: Impl, prefix: str = ""
    ) -> NoReturn:
        concrete_type = self.fcp.get_type(type).unwrap()
        if isinstance(concrete_type, Struct):
            self._generate_struct(concrete_type, extension, prefix)
        elif isinstance(concrete_type, StructField):
            self._generate_signal(concrete_type, extension, prefix)
        elif isinstance(concrete_type, Enum):
            self._generate_enum(type, concrete_type, extension, prefix)  # type: ignore
        else:
            raise KeyError(f"Invalid type {type}")

    def _generate_array_type(
        self, type: ArrayType, field: StructField, extension: Impl, prefix: str = ""
    ) -> NoReturn:
        for i in range(type.size):
            derived_field = copy(field)

            derived_field.type = type.underlying_type
            derived_field.name = field.name + "_" + str(i)
            self._generate_signal(derived_field, extension, prefix)

    def _generate(self, type: Type, extension: Impl, prefix: str = "") -> NoReturn:
        if isinstance(type, StructType) or isinstance(type, EnumType):
            self._generate_compound_type(type, extension, prefix)
        else:
            raise ValueError("Expected StructType or EnumType")

    def generate(self, impl: Impl) -> List[EncodeablePiece]:
        """Generate encoding instructions."""
        self.encoding = []
        self.bitstart = 0

        self._generate(
            StructType(impl.type),  # type: ignore
            impl,
        )
        return self.encoding


Encoder: TypeAlias = Union[PackedEncoder]


def make_encoder(name: str, fcp: FcpV2, ctx: EncoderContext) -> Encoder:
    """Create encoder from encoder name."""
    if name == "packed":
        return PackedEncoder(fcp, ctx)

    raise KeyError(f"Invalid encoding name {name}")
