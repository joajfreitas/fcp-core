import json
from typing import Any
from serde import serde, strict, to_dict


@serde(type_check=strict)
class Field:
    name: str
    value: Any

    def get_type(self):
        return "extension_signal"

    def get_name(self):
        return self.name

    def __repr__(self):
        return str(to_dict(self))
