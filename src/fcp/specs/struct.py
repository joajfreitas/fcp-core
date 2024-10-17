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
