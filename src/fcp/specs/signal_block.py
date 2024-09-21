import json
from typing import List, Dict, Any
from serde import serde, strict, to_dict

from .field import Field


@serde(type_check=strict)
class SignalBlock:
    name: str
    fields: Dict[str, Any]

    def __repr__(self):
        return str(to_dict(self))
