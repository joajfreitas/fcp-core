from beartype.typing import Any
from serde import serde, strict, to_dict


@serde(type_check=strict)
class Field:
    name: str
    value: Any

    def __repr__(self) -> str:
        return str(to_dict(self))
