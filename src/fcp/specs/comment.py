from serde import serde, strict


@serde(type_check=strict)
class Comment:
    """Comment AST node."""

    value: str


def comment_serializer(comment: Comment) -> str:
    """Serialize comment with custom rules in pyserde."""
    if comment is not None:
        return comment.value
    else:
        return None


def comment_deserializer(comment: str) -> Comment:
    """Deserialize comment with custom rules in pyserde."""
    if comment is not None:
        return Comment(value=comment)  # type: ignore
    else:
        return None
