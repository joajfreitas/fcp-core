from typing import *
import datetime
import logging
from serde import Model, fields

from .serde_extend import Any
from .metadata import MetaData
from .comment import Comment


class BroadcastSignal(Model):
    name: fields.Str()
    field: fields.Dict(fields.Str(), Any())
    meta: fields.Optional(MetaData)

    def get_name(self):
        return self.name

    def get_type(self):
        return "broadcast_signal"

    def to_fpi(self):
        def default(name, param):
            defaults = {
                "mux": "",
                "mux_count": 1,
                "scale": 1.0,
                "offset": 0.0,
                "byte_order": "little_endian",
                "start": 0,
                "min_value": 0.0,
                "max_value": 0.0,
            }

            return defaults.get(name) != param

        fields = [
            f"{name}: {param};"
            for name, param in self.field.items()
            if (name not in {"type"}) and default(name, param)
        ]

        return f"\tsignal {self.name} {{\n\t\t" + "\n\t\t".join(fields) + "\n\t};"


class Broadcast(Model):
    """Broadcast object"""

    name: fields.Str()
    field: fields.Dict(fields.Str(), Any())
    signals: fields.List(BroadcastSignal)
    meta: fields.Optional(MetaData)
    comment: Comment

    def get_name(self):
        return self.name

    def get_type(self):
        return "broadcast"

    def get_signal(self, name):
        for signal in self.signals:
            if signal.name == name:
                return signal

        return None

    def get_mux_count(self):
        for signal in self.signals:
            mux_count = signal.field.get("mux_count")
            if mux_count is not None and mux_count != 1:
                return mux_count

        return 1

    def get_mux(self):
        for signal in self.signals:
            mux_count = signal.field.get("mux_count")
            if mux_count is not None and mux_count != 1:
                return signal.field.get("mux")

        return None

    def to_fpi(self):
        return (
            self.field.get("device"),
            (f"/*{self.comment.value}*/\n" if self.comment.value != "" else "")
            + f"broadcast {self.name} {{\n\t"
            + "\n\t".join([f"{name}: {field};" for name, field in self.field.items()])
            + "\n"
            + "\n".join(signal.to_fpi() for signal in self.signals)
            + "\n};\n",
        )

    def __repr__(self):
        return f"<Broadcast name={self.name}"
