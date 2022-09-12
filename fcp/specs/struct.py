from typing import *
import datetime
from serde import Model, fields

from .signal import Signal
from .metadata import MetaData


class Struct(Model):
    """Broadcast object"""

    name: fields.Str()
    signals: fields.List(Signal)
    meta: fields.Optional(MetaData)

    def get_name(self):
        return self.name

    def get_type(self):
        return "struct"

    def to_fpi(self):
        return (
            f"broadcast {self.name} {{\n"
            + "\n".join([f"{name}: {field};" for name, field in self.signals.items()])
            + "\n}\n"
        )

    def __repr__(self):
        return f"<Struct name={self.name}"
