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

# ruff: noqa: D103 D100

from typing_extensions import Self

from fcp.specs.v2 import FcpV2
from fcp.specs.struct import Struct
from fcp.specs.struct_field import StructField
from fcp.specs.type import Type, UnsignedType


class StructFieldBuilder:
    """Builder for StructField."""

    def __init__(self) -> None:
        self.struct_field = StructField("", 0, UnsignedType("u8"))

    def with_name(self, name: str) -> Self:
        """Set the name of the field."""
        self.struct_field.name = name
        return self

    def with_field_id(self, field_id: int) -> Self:
        """Set the field id of the field."""
        self.struct_field.field_id = field_id
        return self

    def with_type(self, type: Type) -> Self:
        """Set the type of the field."""
        self.struct_field.type = type
        return self

    def build(self) -> StructField:
        """Build the StructField."""
        return self.struct_field


class StructBuilder:
    """Builder for Struct."""

    def __init__(self) -> None:
        self.struct = Struct("", [], None)

    def with_name(self, name: str) -> Self:
        """Set the name of the struct."""
        self.struct.name = name
        return self

    def with_field(self, field: StructField) -> Self:
        """Add a field to the struct."""
        self.struct.fields.append(field)
        return self

    def build(self) -> Struct:
        """Build the struct."""
        return self.struct


class FcpV2Builder:
    """Builder for FcpV2."""

    def __init__(self) -> None:
        self.fcp = FcpV2()

    def with_struct(self, struct: Struct) -> Self:
        """Add a struct to the FcpV2."""
        self.fcp.structs.append(struct)
        return self

    def build(self) -> FcpV2:
        """Build the FcpV2."""
        return self.fcp
