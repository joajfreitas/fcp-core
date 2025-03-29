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
from beartype.typing import Dict, List, Any


@serde(type_check=strict)
class Type:
    """Base class for types."""

    def get_length(self) -> int:
        """Type length in bits."""
        raise ValueError("Don't use Type directly")

    def reflection(self) -> List[Dict[str, Any]]:
        """Reflection."""
        raise ValueError("Don't use Type directly")


class NumericType(Type):
    """Numeric type."""

    name: str
    type: str

    def is_signed(self) -> bool:
        """Check that type is signed."""
        return self.name[0] == "i"

    def is_float(self) -> bool:
        """Check that type is a float."""
        return self.name[0] == "f" and self.get_length() == 32

    def is_double(self) -> bool:
        """Check that type is a double."""
        return self.name[0] == "f" and self.get_length() == 64

    def get_length(self) -> int:
        """Type length in bits."""
        return int(self.name[1:])

    def reflection(self) -> List[Dict[str, str]]:
        """Reflection."""
        return [
            {
                "name": self.name,
                "type": self.type,
                "size": 1,
            }
        ]


@serde(type_check=strict)
class UnsignedType(NumericType):
    """Type of unsigned fields."""

    name: str
    type: str

    def __init__(self, name: str):
        self.name = name
        self.type = "unsigned"


@serde(type_check=strict)
class SignedType(NumericType):
    """Type of signed fields."""

    name: str
    type: str

    def __init__(self, name: str):
        self.name = name
        self.type = "signed"


@serde(type_check=strict)
class FloatType(NumericType):
    """Type of float fields."""

    name: str
    type: str

    def __init__(self) -> None:
        self.name = "f32"
        self.type = "float"


@serde(type_check=strict)
class DoubleType(NumericType):
    """Type of float fields."""

    name: str
    type: str

    def __init__(self) -> None:
        self.name = "f64"
        self.type = "double"


@serde(type_check=strict)
class StringType(Type):
    """Type of string fields."""

    type: str

    def __init__(self) -> None:
        self.type = "str"

    def reflection(self) -> List[Dict[str, str]]:
        """Reflection."""
        return [
            {
                "name": "str",
                "type": "str",
                "size": 1,
            }
        ]


@serde(type_check=strict)
class EnumType(Type):
    """Type of enum fields."""

    name: str
    type: str

    def __init__(self, name: str):
        self.name = name
        self.type = "Enum"

    def is_signed(self) -> bool:
        """Signess of enum types."""
        return False

    def reflection(self) -> List[Dict[str, Any]]:
        """Reflection."""
        return [
            {
                "name": self.name,
                "type": "Enum",
                "size": 1,
            }
        ]


@serde(type_check=strict)
class StructType(Type):
    """Type of struct fields."""

    name: str
    type: str

    def __init__(self, name: str):
        self.name = name
        self.type = "Struct"

    def reflection(self) -> List[Dict[str, Any]]:
        """Reflection."""
        return [
            {
                "name": self.name,
                "type": "Struct",
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
