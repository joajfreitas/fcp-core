from typing import Optional
from serde import serde, strict


def comment_serializer(comment):
    if comment is not None:
        return comment.value
    else:
        return None


def comment_deserializer(comment):
    if comment is not None:
        return Comment(comment)
    else:
        return None


@serde(type_check=strict)
class Comment:
    value: str


def comment_serializer(comment: Optional[Comment]) -> Optional[str]:
    if comment is not None:
        return comment.value
    else:
        return None


def comment_deserializer(comment: Optional[str]) -> Optional[Comment]:
    if comment is not None:
        return Comment(value=comment)  # type: ignore
    else:
        return None
