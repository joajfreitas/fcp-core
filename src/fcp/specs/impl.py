from beartype.typing import Any, Dict, List
from serde import serde, strict, to_dict, field

from .signal_block import SignalBlock
from .metadata import MetaData

from ..maybe import Maybe, Nothing, Some, catch


@serde(type_check=strict)
class Impl:
    """Impl AST node."""

    name: str
    protocol: str
    type: str
    fields: Dict[str, Any]
    signals: List[SignalBlock]
    meta: MetaData = field(skip=True)

    def get_signal(self, name: str) -> Maybe[SignalBlock]:
        """Get impl signal."""
        for signal in self.signals:
            if signal.name == name:
                return Some(signal)

        return Nothing()

    def get_field(self, key: str, default: Any = None) -> Maybe[Any]:
        """Get impl field by key."""
        value = self.fields.get(key, default)

        return Some(value) if value is not None else Nothing()

    @catch
    def get_signal_fields(self, name: str) -> Maybe[Dict[str, Any]]:
        """Get impl fields."""
        signal = self.get_signal(name)

        if signal.is_nothing():
            return Nothing()
        else:
            return Some(signal.attempt().fields)

    def __repr__(self) -> str:
        return str(to_dict(self))
