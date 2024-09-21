from serde import serde, strict, field, to_dict
from typing import Optional

from .signal import Signal
from .metadata import MetaData
from .comment import Comment, comment_serializer, comment_deserializer


@serde(type_check=strict)
class Struct:
    """Struct object"""

    name: str
    signals: list[Signal]
    comment: Optional[Comment] = field(
        serializer=comment_serializer, deserializer=comment_deserializer
    )
    meta: Optional[MetaData] = field(skip=True)

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
        comment = f"/*{self.comment.value}*/\n" if self.comment else ""
        return (
            "struct",
            comment
            + f"struct {self.name} {{\n"
            + ";\n".join(map(lambda signal: signal.to_fcp(), self.signals))
            + ";\n};",
        )

    def __repr__(self):
        return str(to_dict(self))
