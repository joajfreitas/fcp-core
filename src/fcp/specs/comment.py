from serde import serde, strict


def comment_serializer(cls, o):
    print("ser", cls, o)
    return None


def comment_deserializer(cls, o):
    print("de", cls, o)
    return None


@serde(type_check=strict)
class Comment:
    value: str
