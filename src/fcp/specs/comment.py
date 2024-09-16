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
