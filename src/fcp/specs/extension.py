from beartype.typing import Any, Dict, List
from serde import serde, strict, to_dict

from .signal_block import SignalBlock

from ..maybe import Maybe, Nothing, Some


@serde(type_check=strict)
class Extension:
    name: str
    protocol: str
    type: str
    fields: Dict[str, Any]
    signals: List[SignalBlock]

    def get_signal(self, name: str) -> Maybe[SignalBlock]:
        for signal in self.signals:
            if signal.name == name:
                return Some(signal)

        return Nothing()

    def get_signal_fields(self, name: str) -> Maybe[Dict[str, Any]]:
        signal = self.get_signal(name)

        if signal.is_nothing():
            return Nothing()
        else:
            return Some(signal.unwrap().fields)

    def get_type(self) -> str:
        return "extension"

    def get_name(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(to_dict(self))
