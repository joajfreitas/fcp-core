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

"""Struct field."""

from beartype.typing import Any, Optional, Dict
from serde import serde, strict, field

from .type import Type
from .metadata import MetaData


@serde(type_check=strict)
class StructField:
    """StructField node."""

    name: str
    field_id: int
    type: Type
    unit: Optional[str] = field(default=None)
    min_value: Optional[float] = field(default=None)
    max_value: Optional[float] = field(default=None)
    meta: Optional[MetaData] = field(skip=True, default=None)

    def __init__(
        self,
        name: str,
        field_id: int,
        type: Type,
        unit: Optional[str] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        meta: Optional[MetaData] = None,
    ) -> None:
        self.name = name
        self.field_id = field_id
        self.type = type
        self.unit = unit
        self.min_value = min_value
        self.max_value = max_value
        self.meta = meta

    def reflection(self) -> Dict[str, Any]:
        """Reflection."""
        return {
            "name": self.name,
            "field_id": self.field_id,
            "type": self.type.reflection(),
            "unit": self.unit,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "meta": self.meta.reflection() if self.meta else None,
        }

    def __repr__(self) -> str:
        return f"<Signal name={self.name} type={self.type}>"
