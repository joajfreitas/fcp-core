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
