from beartype.typing import Any, Dict
from serde import serde, strict, to_dict

from .metadata import MetaData


@serde(type_check=strict)
class SignalBlock:
    """SignalBlock AST node."""

    name: str
    fields: Dict[str, Any]
    meta: MetaData

    def __repr__(self) -> str:
        return str(to_dict(self))
