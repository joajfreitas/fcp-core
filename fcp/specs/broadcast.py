from typing import *
import datetime
from serde import Model, fields

from .serde_extend import Any
from .metadata import MetaData


class Broadcast(Model):
    """Broadcast object"""

    name: fields.Str()
    field: fields.Dict(fields.Str(), Any())
    meta: fields.Optional(MetaData)

    def get_name(self):
        return self.name

    def get_type(self):
        return "broadcast"

    def to_fpi(self):
        return (
            f"broadcast {self.name} {{\n"
            + "\n".join([f"{name}: {field};" for name, field in self.field.items()])
            + "\n}\n"
        )

    def __repr__(self):
        return f"<Broadcast name={self.name}"
