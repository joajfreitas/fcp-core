from beartype.typing import Any, Dict, List
from serde import serde, strict, to_dict

from .signal_block import SignalBlock


@serde(type_check=strict)
class Extension:
    name: str
    protocol: str
    type: str
    fields: Dict[str, Any]
    signals: List[SignalBlock]

    def get_signal(self, name: str) -> Optional[SignalBlock]:
        for signal in self.signals:
            if signal.name == name:
                return signal

        return None

    def get_signal_fields(self, name: str) -> Optional[dict[str, Any]]:
        signal = self.get_signal(name)

        if signal is None:
            return {}
        else:
            return signal.fields

    def get_type(self) -> str:
        return "extension"

    def get_name(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(to_dict(self))
