from beartype.typing import Any, Dict
from serde import serde, strict, to_dict


@serde(type_check=strict)
class SignalBlock:
    name: str
    fields: Dict[str, Any]

    def __repr__(self) -> str:
        return str(to_dict(self))
