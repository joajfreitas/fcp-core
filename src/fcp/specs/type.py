"""Type."""

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

from serde import serde, strict
from beartype.typing import Union
from typing_extensions import Self
from enum import Enum


@serde(type_check=strict)
class BuiltinType:
    """fcp builtin types."""

    name: str

    def get_length(self) -> int:
        """Type length in bits."""
        return int(self.name[1:])

    def is_signed(self) -> bool:
        """Check that type is signed."""
        return self.name[0] == "i"

    def is_unsigned(self) -> bool:
        """Check that type is unsigned."""
        return self.name[0] == "u"

    def is_float(self) -> bool:
        """Check that type is float."""
        return self.name[0] == "f"

    def is_double(self) -> bool:
        """Check that type is double."""
        return self.name[0] == "d"


class ComposedTypeCategory(Enum):
    """Category of composed types."""

    Enum = "Enum"
    Struct = "Struct"


@serde(type_check=strict)
class ComposedType:
    """fcp type for user defined types such as structs and enums."""

    name: str
    category: ComposedTypeCategory

    def is_signed(self) -> bool:
        """Check that type is signed."""
        if self.category == ComposedTypeCategory.Enum:
            return False
        else:
            raise ValueError("Signess of struct is meaningless")


@serde(type_check=strict)
class ArrayType:
    """fcp array type."""

    type: Union[BuiltinType, ComposedType, Self]
    size: int

    def get_length(self) -> int:
        """Type length in bits."""
        return int(self.type.get_length() * self.size)


Type = Union[BuiltinType, ArrayType, ComposedType]
