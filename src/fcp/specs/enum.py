from serde import serde, strict, field
from beartype.typing import Optional, List, Tuple

from .metadata import MetaData
from .comment import Comment, comment_serializer, comment_deserializer


@serde(type_check=strict)
class Enumeration:
    """Enum member AST node."""

    name: str
    value: int
    comment: Optional[Comment] = field(
        default=None, serializer=comment_serializer, deserializer=comment_deserializer
    )
    meta: Optional[MetaData] = field(default=None, skip=True)


@serde(type_check=strict)
class Enum:
    """Enum AST node.

    Somewhat similar to a C enum.
    """

    name: str
    enumeration: List[Enumeration]
    comment: Optional[Comment] = field(
        default=None, serializer=comment_serializer, deserializer=comment_deserializer
    )
    meta: Optional[MetaData] = field(default=None, skip=True)

    def __repr__(self) -> str:
        return "Enum name: {}".format(self.name)
