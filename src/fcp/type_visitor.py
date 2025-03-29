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

"""Visitor for the fcp type hierarchy."""

from beartype.typing import Any, List

from .specs.v2 import FcpV2
from .specs import type


class TypeVisitor:
    """Visitor for the fcp type hierarchy."""

    def __init__(self, fcp: FcpV2) -> None:
        self.fcp = fcp

    def struct(self, t: type.StructType, fields: List[Any]) -> Any:
        """Visit a struct type."""
        return None

    def enum(self, t: type.EnumType) -> Any:
        """Visit an enum type."""
        return None

    def unsigned(self, t: type.BuiltinType) -> Any:
        """Visit an unsigned type."""
        return None

    def signed(self, t: type.BuiltinType) -> Any:
        """Visit a signed type."""
        return None

    def float(self, t: type.BuiltinType) -> Any:
        """Visit a float type."""
        return None

    def double(self, t: type.BuiltinType) -> Any:
        """Visit a double type."""
        return None

    def string(self, t: type.StringType) -> Any:
        """Visit a string type."""
        return None

    def array(self, t: type.ArrayType, inner: type.Type) -> Any:
        """Visit an array type."""
        return None

    def dynamic_array(self, t: type.DynamicArrayType, inner: type.Type) -> Any:
        """Visit a dynamic array type."""
        return None

    def optional(self, t: type.OptionalType, inner: type.Type) -> Any:
        """Visit an optional type."""
        return None

    def visit(self, t: type.Type) -> Any:
        """Visits the hierarchy of an fcp type."""
        if isinstance(t, type.StructType):
            fields = [
                self.visit(field.type) for field in self.fcp.get_type(t).unwrap().fields
            ]
            return self.struct(t, fields)
        elif isinstance(t, type.EnumType):
            return self.enum(t)
        elif isinstance(t, type.BuiltinType):
            if t.is_unsigned():
                return self.unsigned(t)
            elif t.is_signed():
                return self.signed(t)
            elif t.is_float():
                return self.float(t)
            elif t.is_double():
                return self.double(t)
        elif isinstance(t, type.StringType):
            return self.string(t)
        elif isinstance(t, type.ArrayType):
            return self.array(t, self.visit(t.underlying_type))
        elif isinstance(t, type.DynamicArrayType):
            return self.dynamic_array(t, self.visit(t.underlying_type))
        elif isinstance(t, type.OptionalType):
            return self.optional(t, self.visit(t.underlying_type))

        raise ValueError("Unexpected type: " + str(t))
