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

"""Enum."""

from serde import serde, strict, field
from beartype.typing import Optional, List, Tuple, Dict, Any
import math

from .metadata import MetaData


@serde(type_check=strict)
class Enumeration:
    """Enum member AST node."""

    name: str
    value: int
    meta: Optional[MetaData] = field(default=None, skip=True)

    def reflection(self) -> Dict[str, Any]:
        """Reflection."""
        return {"name": self.name, "value": self.value, "meta": self.meta.reflection()}


@serde(type_check=strict)
class Enum:
    """Enum AST node.

    Somewhat similar to a C enum.
    """

    name: str
    enumeration: List[Enumeration]
    meta: Optional[MetaData] = field(default=None, skip=True)

    def get_packed_size(self) -> int:
        """Get packed enum size."""
        return math.ceil(math.log2(max([x.value for x in self.enumeration])) + 1)

    def reflection(self) -> Dict[str, Any]:
        """Reflection."""
        return {
            "name": self.name,
            "enumeration": [
                enumeration.reflection() for enumeration in self.enumeration
            ],
            "meta": self.meta.reflection(),
        }

    def __repr__(self) -> str:
        return "Enum name: {}".format(self.name)
