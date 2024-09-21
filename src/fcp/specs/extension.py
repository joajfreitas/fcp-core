from typing import Any
from serde import serde, strict, to_dict

from .signal_block import SignalBlock


@serde(type_check=strict)
class Extension:
    name: str
    type: str
    fields: dict[str, Any]
    signals: list[SignalBlock]

    def get_type(self) -> str:
        return "extension"

    def get_name(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(to_dict(self))
