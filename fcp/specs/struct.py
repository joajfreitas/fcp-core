import datetime
from serde import Model, fields

from .signal import Signal
from .metadata import MetaData
from .comment import Comment


class Struct(Model):
    """Broadcast object"""

    name: fields.Str()
    signals: fields.List(Signal)
    meta: fields.Optional(MetaData)
    comment: Comment

    def get_name(self):
        return self.name

    def get_type(self):
        return "struct"

    def get_signal(self, name):
        for signal in self.signals:
            if signal.name == name:
                return signal

        return None

    def to_fcp(self):
        return (
            "struct",
            (f"/*{self.comment.value}*/\n" if self.comment.value != "" else "")
            + f"struct {self.name} {{\n"
            + ";\n".join(map(lambda signal: signal.to_fcp(), self.signals))
            + ";\n};",
        )

    def __repr__(self):
        return f"<Struct name={self.name}"
