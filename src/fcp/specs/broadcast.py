import serde
from typing import Any, Optional, Union

from .metadata import MetaData
from .comment import Comment


@serde.serde(type_check=serde.strict)
class BroadcastSignal:
    name: str
    field: dict[str, Any]
    meta: Optional[MetaData] = None

    def get_name(self) -> str:
        return self.name

    def get_type(self) -> str:
        return "broadcast_signal"

    def to_fpi(self) -> str:
        def default(name: str, param: Any) -> bool:
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

            return bool(defaults.get(name) != param)

        fields = [
            f"{name}: {param};"
            for name, param in self.field.items()
            if (name not in {"type"}) and default(name, param)
        ]

        return f"\tsignal {self.name} {{\n\t\t" + "\n\t\t".join(fields) + "\n\t};"


@serde.serde(type_check=serde.strict)
class Broadcast:
    """Broadcast object"""

    name: str
    field: dict[str, Any]
    signals: list[BroadcastSignal]
    comment: Comment
    meta: Optional[MetaData] = serde.field(skip=True)

    def get_name(self) -> str:
        return self.name

    def get_type(self) -> str:
        return "broadcast"

    def get_signal(self, name: str) -> Optional[BroadcastSignal]:
        for signal in self.signals:
            if signal.name == name:
                return signal

        return None

    def get_mux_count(self) -> int:
        for signal in self.signals:
            mux_count = signal.field.get("mux_count")
            if mux_count is not None and mux_count != 1:
                return int(mux_count)

        return 1

    def get_mux(self) -> Union[Any, None]:
        for signal in self.signals:
            mux_count = signal.field.get("mux_count")
            if mux_count is not None and mux_count != 1:
                return signal.field.get("mux")

        return None

    def to_fpi(self) -> tuple[Any, str]:
        return (
            self.field.get("device"),
            (f"/*{self.comment.value}*/\n" if self.comment.value != "" else "")
            + f"broadcast {self.name} {{\n\t"
            + "\n\t".join([f"{name}: {field};" for name, field in self.field.items()])
            + "\n"
            + "\n".join(signal.to_fpi() for signal in self.signals)
            + "\n};\n",
        )

    def __repr__(self) -> str:
        return f"<Broadcast name={self.name}"
