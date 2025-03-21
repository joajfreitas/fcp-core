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

"""Type."""

from __future__ import annotations

from serde import serde, strict
from beartype.typing import Union, Dict, List, Any
from typing_extensions import Self, TypeAlias
from enum import Enum


@serde(type_check=strict)
class Type:
    """Base class for types."""

    def get_length(self) -> int:
        """Type length in bits."""
        raise ValueError("Don't use Type directly")

    def reflection(self) -> List[Dict[str, Any]]:
        """Reflection."""
        raise ValueError("Don't use Type directly")


@serde(type_check=strict)
class BuiltinType(Type):
    """fcp builtin types."""

    name: str
    type: str

    def __init__(self, name: str):
        self.name = name
        self.type = "Builtin"

    def get_length(self) -> int:
        """Type length in bits."""
        if self.is_str():
            raise ValueError("No length for dynamic strings")
        return int(self.name[1:])

    def is_signed(self) -> bool:
        """Check that type is signed."""
        return self.name[0] == "i"

    def is_unsigned(self) -> bool:
        """Check that type is unsigned."""
        return self.name[0] == "u"

    def is_float(self) -> bool:
        """Check that type is a float."""
        return self.name[0] == "f" and int(self.name[1:]) == 32

    def is_double(self) -> bool:
        """Check that type is a double."""
        return self.name[0] == "f" and int(self.name[1:]) == 64

    def is_str(self) -> bool:
        """Check that type is a string."""
        return self.name == "str"

    def reflection(self) -> List[Dict[str, str]]:
        """Reflection."""
        return [
            {
                "name": self.name,
                "type": self.type,
                "size": 1,
            }
        ]


class ComposedTypeCategory(Enum):
    """Category of composed types."""

    Enum = "Enum"
    Struct = "Struct"


@serde(type_check=strict)
class ComposedType(Type):
    """fcp type for user defined types such as structs and enums."""

    name: str
    type: ComposedTypeCategory

    def __init__(self, name: str, type: ComposedTypeCategory):
        self.name = name
        self.type = type

    def is_signed(self) -> bool:
        """Check that type is signed."""
        if self.type == ComposedTypeCategory.Enum:
            return False
        else:
            raise ValueError("Signess of struct is meaningless")

    def reflection(self) -> List[Dict[str, str]]:
        """Reflection."""
        return [
            {
                "name": self.name,
                "type": str(self.type).split(".")[1],
                "size": 1,
            }
        ]


@serde(type_check=strict)
class ArrayType(Type):
    """fcp array type."""

    underlying_type: Type
    size: int
    type: str

    def __init__(self, underlying_type: Type, size: int):
        self.underlying_type = underlying_type
        self.size = size
        self.type = "Array"

    def get_length(self) -> int:
        """Type length in bits."""
        return int(self.underlying_type.get_length() * self.size)

    def reflection(self) -> List[Dict[str, Any]]:
        """Reflection."""
        return [
            {
                "name": self.type,
                "type": self.type,
                "size": self.size,
            }
        ] + self.underlying_type.reflection()


@serde(type_check=strict)
class DynamicArrayType(Type):
    """fcp array type."""

    underlying_type: Type
    type: str

    def __init__(self, underlying_type: Type):
        self.underlying_type = underlying_type
        self.type = "DynamicArray"

    def get_length(self) -> int:
        """Type length in bits."""
        raise ValueError("Cannot compute the size of a dynamic array")

    def reflection(self) -> List[Dict[str, Any]]:
        """Reflection."""
        return [
            {
                "name": self.type,
                "type": self.type,
                "size": 1,
            }
        ] + self.underlying_type.reflection()


@serde(type_check=strict)
class OptionalType(Type):
    """fcp optional type."""

    underlying_type: Type
    type: str

    def __init__(self, underlying_type: Type):
        self.underlying_type = underlying_type
        self.type = "Optional"

    def get_length(self) -> int:
        """Type length in bits."""
        raise ValueError("Cannot compute the size of an Optional ")

    def reflection(self) -> List[Dict[str, str]]:
        """Reflection."""
        return [
            {
                "name": self.type,
                "type": self.type,
                "size": 1,
            }
        ] + self.underlying_type.reflection()
