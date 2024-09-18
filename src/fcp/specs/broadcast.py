from serde import serde, strict
from typing import Any, Optional, Union

from .metadata import MetaData
from .comment import Comment


@serde(type_check=strict)
class BroadcastSignal:
    name: str
    field: dict[str, Any]
    meta: Optional[MetaData] = None

    def get_name(self) -> str:
        return self.name

    def get_type(self) -> str:
        return "broadcast_signal"


@serde(type_check=strict)
class Broadcast:
    """Broadcast object"""

    name: str
    field: dict[str, Any]
    signals: list[BroadcastSignal]
    comment: Comment
    meta: Optional[MetaData] = None

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

    def __repr__(self) -> str:
        return f"<Broadcast name={self.name}"
