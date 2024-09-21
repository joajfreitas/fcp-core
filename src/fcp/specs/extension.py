import json
from typing import List, Dict, Any
from serde import serde, strict, to_dict

from .field import Field
from .signal_block import SignalBlock


@serde(type_check=strict)
class Extension:
    name: str
    type: str
    fields: Dict[str, Any]
    signals: List[SignalBlock]

    def get_type(self):
        return "extension"

    def get_name(self):
        return self.name

    def __repr__(self):
        return str(to_dict(self))
