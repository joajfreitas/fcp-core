# Copyright (c) 2025 the fcp AUTHORS.
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

"""Describe."""

from beartype.typing import List, Any, Tuple

from .specs.v2 import FcpV2
from .specs.type import Type
from .type_visitor import TypeVisitor
from .specs import type


class DescribeVisitor(TypeVisitor):
    """Visitor to describe a type encoding."""

    def struct(self, t: type.StructType, fields: List[Any], name: str) -> Any:
        """Visit a struct type."""
        return fields

    def enum(self, t: type.EnumType, name: str) -> Any:
        """Visit an enum type."""
        e = self.fcp.get_enum(t.name).unwrap()
        return name, t.name, e.get_packed_size()

    def unsigned(self, t: type.UnsignedType, name: str) -> Any:
        """Visit an unsigned type."""
        return name, t.name, t.get_length()

    def signed(self, t: type.SignedType, name: str) -> Any:
        """Visit a signed type."""
        return name, t.name, t.get_length()

    def float(self, t: type.FloatType, name: str) -> Any:
        """Visit a float type."""
        return name, t.name, t.get_length()

    def double(self, t: type.DoubleType, name: str) -> Any:
        """Visit a double type."""
        return name, t.name, t.get_length()

    def string(self, t: type.StringType, name: str) -> Any:
        """Visit a string type."""
        return [("size", 32), ("content", 8)]

    def array(self, t: type.ArrayType, inner: type.Type, name: str) -> Any:
        """Visit an array type."""
        return [inner for _ in range(t.size)]

    def dynamic_array(
        self, t: type.DynamicArrayType, inner: type.Type, name: str
    ) -> Any:
        """Visit a dynamic array type."""
        return [("size", 32), inner]

    def optional(self, t: type.OptionalType, inner: type.Type, name: str) -> Any:
        """Visit an optional type."""
        return [("has_value", 1), inner]


def walk(xs: List[Any] | Any, level: int = -1) -> str:
    """Convert the description information to string."""
    ss = ""
    if isinstance(xs, list):
        for x in xs:
            ss += walk(x, level + 1)
    else:
        ss += level * "\t" + f"{xs}\n"

    return ss


def flatten(xs: List[List[Any]]) -> List[Any]:
    """Flatten a list of lists."""
    if isinstance(xs, list):
        ys = []
        for x in xs:
            ys += flatten(x)

        return ys
    else:
        return [xs]


class Describer:
    """Describer."""

    def __init__(self) -> None:
        self.bitcount = 0
        self.previous_bitcount = 0
        self.references: List[str] = []

    def _add_reference(self, name: str) -> int:
        """Add a reference to the list."""
        self.references.append(name)
        return len(self.references) - 1

    def _block(self, name: str, length: int) -> str:
        padding = int((2 * length - len(name)) / 2)
        return padding * " " + name + padding * " "

    def _section(self, name: str, length: int) -> str:
        current_word_size = self.bitcount - self.previous_bitcount
        if current_word_size + length > 32:
            overflow = -(current_word_size - length + 32)
            self.previous_bitcount = self.bitcount + 32
            self.bitcount = overflow
            return (
                self._block(name, (32 - current_word_size))
                + "\n"
                + self._block("", overflow)
                + "|"
            )

        if len(name) >= 2 * length - 1:
            name = str(self._add_reference(name))
        return self._block(name, length) + "|"

    def describe(self, xs: List[Tuple[str, str, int]]) -> str:
        """Describe the type."""
        ss = " 0 1 2 3 4 5 6 7 8 9 A B C D E F 0 1 2 3 4 5 6 7 8 9 A B C D E F \n"

        ss += "|"
        for name, _, bitsize in xs:
            ss += self._section(name, bitsize)
            self.bitcount += bitsize
            if self.bitcount - self.previous_bitcount >= 32:
                ss += "\n"
                ss += "|"
                self.previous_bitcount = self.bitcount

        if len(self.references) > 0:
            ss += "\n"

        for i, name in enumerate(self.references):
            ss += f"\n{i}: {name}"
        return ss


def describe(schema: FcpV2, type: Type) -> str:
    """Describe a type."""
    describe_visitor = DescribeVisitor(schema)
    xs = flatten(describe_visitor.visit(type))

    return Describer().describe(xs)
