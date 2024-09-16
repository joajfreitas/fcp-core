from serde import serde, strict, field
from typing import Optional

from .metadata import MetaData
from .comment import Comment, comment_serializer, comment_deserializer


@serde(type_check=strict)
class Enumeration:
    name: str
    value: int
    comment: Optional[Comment] = field(default=None, serializer=comment_serializer, deserializer=comment_deserializer)
    meta: Optional[MetaData] = field(default=None)


@serde(type_check=strict)
class Enum:
    """Fcp Enum. C lookalike for FCP type definitions with name-value
    associations.
    """

    name: str
    enumeration: list[Enumeration]
    comment: Optional[Comment] = field(default=None, serializer=comment_serializer, deserializer=comment_deserializer)
    meta: Optional[MetaData] = field(default=None, skip=True)

    def get_name(self) -> str:
        return self.name

    def get_type(self) -> str:
        return "enum"

    def to_fcp(self) -> tuple[str, str]:
        return (
            "enum",
            (f"/*{self.comment.value}*/\n" if self.comment.value != "" else "")
            + f"enum {self.name} {{\n\t"
            + "\n\t".join([f"{enum.name}: {enum.value};" for enum in self.enumeration])
            + "\n};",
        )

    def __repr__(self) -> str:
        return "name: {}".format(self.name)
