from serde import serde, strict


@serde(type_check=strict)
class Comment:
    value: str
