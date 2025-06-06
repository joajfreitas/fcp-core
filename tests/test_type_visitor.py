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

from beartype.typing import List

from fcp.type_visitor import TypeVisitor
from fcp.specs import type
from fcp.parser import get_fcp_from_string


class TestTypeVisitor(TypeVisitor):
    """Test type visitor."""

    def struct(self, t: type.StructType, fields: List[type.Type], name: str) -> str:
        """Visit a struct type."""
        return "struct: " + " ".join(fields)

    def enum(self, t: type.EnumType, name: str) -> str:
        """Visit an enum type."""
        return "enum"

    def unsigned(self, t: type.UnsignedType, name: str) -> str:
        """Visit an unsigned type."""
        return "unsigned"

    def signed(self, t: type.SignedType, name: str) -> str:
        """Visit a signed type."""
        return "signed"

    def float(self, t: type.FloatType, name: str) -> str:
        """Visit a float type."""
        return "float"

    def double(self, t: type.DoubleType, name: str) -> str:
        """Visit a double type."""
        return "double"

    def string(self, t: type.StringType, name: str) -> str:
        """Visit a string type."""
        return "string"

    def array(self, t: type.ArrayType, inner: type.Type, name: str) -> str:
        """Visit an array type."""
        return "array"

    def dynamic_array(
        self, t: type.DynamicArrayType, inner: type.Type, name: str
    ) -> str:
        """Visit a dynamic array type."""
        return "dynamic_array"

    def optional(self, t: type.OptionalType, inner: type.Type, name: str) -> str:
        """Visit an optional type."""
        return "optional"


def test_type_visitor() -> None:
    fcp = get_fcp_from_string(
        """
version: "3"

struct S1 {
    field1 @0: u8,
    field2 @1: i8,
}
"""
    ).unwrap()

    test_visitor = TestTypeVisitor(fcp)

    assert test_visitor.visit(type.StructType("S1")) == "struct: unsigned signed"
