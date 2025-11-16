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
from typing_extensions import Self, TypeAlias, Set, Tuple
from math import log2, ceil
from copy import copy

from .specs.struct import Struct
from .specs.enum import Enum
from .specs.struct_field import StructField
from .specs.type import (
    Type,
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
        composite_type: Optional[str] = Nothing(),
        nested_fields: Optional[List["Value"]] = None,
    ) -> None:
        self.name = name
        self.type = type
        self.bitstart = bitstart
        self.bitlength = bitlength
        self.endianess = endianess
        self.extended_data = extended_data
        self.unit = unit
        self.composite_type = composite_type
        self.nested_fields = nested_fields or []

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

    def __init__(
        self, unroll_arrays: bool = False, preserve_nested_structs: bool = False
    ):
        self.unroll_arrays = unroll_arrays
        self.preserve_nested_structs = preserve_nested_structs

    def with_unroll_arrays(self, unroll_arrays: bool) -> Self:
        """Unroll arrays into N scalar values."""
        this = copy(self)
        this.unroll_arrays = unroll_arrays
        return this

    def with_preserve_nested_structs(self, preserve: bool) -> Self:
        """Preserve nested struct hierarchy instead of flattening."""
        this = copy(self)
        this.preserve_nested_structs = preserve
        return this


EncoderContext: TypeAlias = Union[PackedEncoderContext]


class PackedEncoder:
    """Packed encoder. Packs all bits really tight. Only handles static length data.

    Supports two modes controlled by PackedEncoderContext:
    - preserve_nested_structs=False (default): Flattens nested structs into individual signals
    - preserve_nested_structs=True: Preserves struct hierarchy in nested_fields attribute

    Arrays can be unrolled into individual elements when unroll_arrays=True.

    """

    def __init__(self, fcp: FcpV2, ctx: PackedEncoderContext):
        self.fcp = fcp
        self.ctx = ctx
        self.encoding: List[Value] = []
        self.bitstart = 0

    def _get_type_length(
        self, fcp: FcpV2, type: Type, _seen: Optional[Set[Tuple[str, str]]] = None
    ) -> int:
        if _seen is None:
            _seen = set()
        if (
            isinstance(type, UnsignedType)
            or isinstance(type, SignedType)
            or isinstance(type, FloatType)
            or isinstance(type, DoubleType)
        ):
            return type.get_length()
        elif isinstance(type, ArrayType):
            return int(
                type.size * self._get_type_length(fcp, type.underlying_type, _seen)
            )
        elif isinstance(type, EnumType):
            return int(
                2 ** ceil(log2(fcp.get_enum(type.name).unwrap().get_packed_size()))
            )
        elif isinstance(type, StructType):
            key = ("struct", type.name)
            if key in _seen:
                raise ValueError(f"Recursive type {type.name}")
            _seen.add(key)
            struct = fcp.get_struct(type.name).unwrap()
            total = 0
            for field in sorted(struct.fields, key=lambda f: f.field_id):
                total += self._get_type_length(fcp, field.type, _seen)
            _seen.remove(key)
            return total
        else:
            raise ValueError("Error computing type length for type " + str(type))

    def _generate_struct(
        self, struct: Struct, extension: Impl, prefix: str = ""
    ) -> None:
        """Generate struct encoding, optionally preserving nested structure."""
        for field in sorted(struct.fields, key=lambda field: field.field_id):
            if isinstance(field.type, StructType):
                if self.ctx.preserve_nested_structs:
                    nested_struct = self.fcp.get_struct(field.type.name).unwrap()
                    nested_values = self._generate_struct_recursive(
                        nested_struct, extension, self.bitstart
                    )

                    total_bitlength = sum(v.bitlength for v in nested_values)

                    self.encoding.append(
                        Value(
                            name=field.name,
                            type=field.type,
                            bitstart=self.bitstart,
                            bitlength=total_bitlength,
                            composite_type=Some(field.type.name),
                            nested_fields=nested_values,
                            unit=field.unit,
                        )
                    )
                    self.bitstart += total_bitlength
                else:
                    self._generate_nested_struct(field, extension, prefix)
            else:
                self._generate_signal(field, extension, prefix)

    def _generate_nested_struct(
        self, field: StructField, extension: Impl, prefix: str = ""
    ) -> None:
        """Flatten a nested struct into scalar Values with flattened names.

        Used when preserve_nested_structs=False (default behavior). Recursively
        processes nested structs and creates Values with names like 'parent::child'.

        Args:
            field: The struct field to flatten
            extension: The implementation extension
            prefix: Naming prefix for the flattened fields

        """
        if isinstance(field.type, StructType):
            struct_name = field.type.name
            struct = self.fcp.get_struct(struct_name).unwrap()
        else:
            raise TypeError(f"Expected StructType, got {type(field.type)}")

        for nested_field in sorted(struct.fields, key=lambda f: f.field_id):
            nested_prefix = prefix + field.name + "::"

            if isinstance(nested_field.type, StructType):
                nested_struct_field = StructField(
                    name=nested_field.name,
                    field_id=nested_field.field_id,
                    type=nested_field.type,
                    unit=nested_field.unit,
                )
                self._generate_nested_struct(
                    nested_struct_field, extension, nested_prefix
                )
            else:
                type_length = self._get_type_length(self.fcp, nested_field.type)
                fields_data: Dict[str, Any] = (
                    extension.get_signal(nested_field.name)
                    .and_then(lambda s: Some(s.fields))
                    .unwrap_or({})
                )
                self.encoding.append(
                    Value(
                        name=nested_prefix + nested_field.name,
                        type=nested_field.type,
                        bitstart=self.bitstart,
                        bitlength=type_length,
                        endianess=fields_data.get("endianess") or "little",
                        unit=nested_field.unit,
                        extended_data=fields_data,
                    )
                )
                self.bitstart += type_length

    def _generate_struct_recursive(
        self, struct: Struct, extension: Impl, parent_bitstart: int = 0
    ) -> List[Value]:
        """Generate Values for a struct, preserving nested structure.

        This method is used when preserve_nested_structs=True or when processing
        arrays of structs. It recursively processes nested structs and returns
        a list of Value objects with their nested_fields populated.

        Args:
            struct: The struct to process
            extension: The implementation extension
            parent_bitstart: The starting bit position for this struct

        Returns:
            List of Value objects representing the struct's fields

        """
        result = []
        bitstart = parent_bitstart

        for field in sorted(struct.fields, key=lambda f: f.field_id):
            if isinstance(field.type, StructType):
                nested_struct = self.fcp.get_struct(field.type.name).unwrap()
                nested_values = self._generate_struct_recursive(
                    nested_struct, extension, bitstart
                )

                total_bitlength = sum(v.bitlength for v in nested_values)

                result.append(
                    Value(
                        name=field.name,
                        type=field.type,
                        bitstart=bitstart,
                        bitlength=total_bitlength,
                        composite_type=Some(field.type.name),
                        nested_fields=nested_values,
                        unit=field.unit,
                    )
                )
                bitstart += total_bitlength
            else:
                type_length = self._get_type_length(self.fcp, field.type)
                fields_data: Dict[str, Any] = (
                    extension.get_signal(field.name)
                    .and_then(lambda s: Some(s.fields))
                    .unwrap_or({})
                )

                result.append(
                    Value(
                        name=field.name,
                        type=field.type,
                        bitstart=bitstart,
                        bitlength=type_length,
                        endianess=fields_data.get("endianess") or "little",
                        unit=field.unit,
                        extended_data=fields_data,
                    )
                )
                bitstart += type_length

        return result

    def _generate_signal(
        self, field: "StructField", extension: "Impl", prefix: str = ""
    ) -> None:
        """Generate a scalar signal Value (no nested struct handling here)."""
        if isinstance(field.type, ArrayType) and self.ctx.unroll_arrays:
            self._generate_array_type(field.type, field, extension, prefix)
            return

        type_length = self._get_type_length(self.fcp, field.type)
        fields: Dict[str, Any] = (
            extension.get_signal(field.name)
            .and_then(lambda s: Some(s.fields))
            .unwrap_or({})
        )
        self.encoding.append(
            Value(
                name=prefix + field.name,
                type=field.type,
                bitstart=self.bitstart,
                bitlength=type_length,
                endianess=fields.get("endianess") or "little",
                unit=field.unit,
                extended_data=fields,
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

            if isinstance(type.underlying_type, StructType):
                struct = self.fcp.get_struct(type.underlying_type.name).unwrap()

                nested_values = self._generate_struct_recursive(
                    struct, extension, self.bitstart
                )

                total_bitlength = sum(v.bitlength for v in nested_values)

                self.encoding.append(
                    Value(
                        name=prefix + derived_field.name,
                        type=type.underlying_type,
                        bitstart=self.bitstart,
                        bitlength=total_bitlength,
                        composite_type=Some(type.underlying_type.name),
                        nested_fields=nested_values,
                        unit=derived_field.unit,
                    )
                )
                self.bitstart += total_bitlength
            else:
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
