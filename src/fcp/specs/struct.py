"""Struct."""

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

from beartype.typing import Optional, List, Tuple
import serde

from .struct_field import StructField
from .metadata import MetaData
from .comment import Comment, comment_serializer, comment_deserializer


@serde.serde(type_check=serde.strict)
class Struct:
    """Struct object."""

    name: str
    fields: List[StructField]
    comment: Optional[Comment] = serde.field(
        default=None, serializer=comment_serializer, deserializer=comment_deserializer
    )
    meta: Optional[MetaData] = serde.field(default=None, skip=True)

    def get_field(self, name: str) -> Optional[StructField]:
        """Get struct field."""
        for field in self.fields:
            if field.name == name:
                return field

        return None

    def __repr__(self) -> str:
        return str(serde.to_dict(self))
