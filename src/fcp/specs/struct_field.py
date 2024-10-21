"""Struct field."""

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

from beartype.typing import Any, Optional, Union
from serde import serde, strict, field

from .type import Type
from .metadata import MetaData
from .comment import Comment, comment_serializer, comment_deserializer


@serde(type_check=strict)
class StructField:
    """StructField node."""

    name: str
    field_id: int
    type: Type
    unit: Optional[str] = None
    comment: Optional[Comment] = field(
        default=None, serializer=comment_serializer, deserializer=comment_deserializer
    )
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    meta: Optional[MetaData] = field(skip=True, default=None)

    def __repr__(self) -> str:
        return f"<Signal name={self.name} type={self.type}>"
