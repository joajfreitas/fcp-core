from beartype.typing import Any, Dict, List
from serde import serde, strict, to_dict, field

from .signal_block import SignalBlock
from .metadata import MetaData

from ..maybe import Maybe, Nothing, Some, catch


@serde(type_check=strict)
class Extension:
    name: str
    protocol: str
    type: str
    fields: Dict[str, Any]
    signals: List[SignalBlock]
    meta: MetaData = field(skip=True)

    def get_signal(self, name: str) -> Maybe[SignalBlock]:
        for signal in self.signals:
            if signal.name == name:
                return Some(signal)

        return Nothing()

    @catch
    def get_signal_fields(self, name: str) -> Maybe[Dict[str, Any]]:
        signal = self.get_signal(name)

        if signal.is_nothing():
            return Nothing()
        else:
            return Some(signal.attempt().fields)

    def get_type(self) -> str:
        return "extension"

    def get_name(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(to_dict(self))
