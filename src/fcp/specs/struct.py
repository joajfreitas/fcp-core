from serde import serde, strict
from typing import Optional

from .signal import Signal
from .metadata import MetaData
from .comment import Comment


@serde(type_check=strict)
class Struct:
    """Broadcast object"""

    name: str
    signals: list[Signal]
    meta: Optional[MetaData]
    comment: Optional[Comment]

    def get_name(self) -> str:
        return self.name

    def get_type(self) -> str:
        return "struct"

    def get_signal(self, name: str) -> Optional[Signal]:
        for signal in self.signals:
            if signal.name == name:
                return signal

        return None

    def to_fcp(self) -> tuple[str, str]:
        return (
            "struct",
            (f"/*{self.comment.value}*/\n" if self.comment.value != "" else "")
            + f"struct {self.name} {{\n"
            + ";\n".join(map(lambda signal: signal.to_fcp(), self.signals))
            + ";\n};",
        )

    def __repr__(self) -> str:
        return f"<Struct name={self.name}"
