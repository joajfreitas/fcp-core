"""Impl."""

# Copyright (c) 2024 the fcp AUTHORS.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


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

    def reflection(self) -> Dict[str, Any]:
        """Reflection."""
        return {
            "name": self.name,
            "protocol": self.protocol,
            "type": self.type,
            "fields": [
                {"name": key, "value": str(value)} for key, value in self.fields.items()
            ],
            "signals": [signal.refection() for signal in self.signals],
            "meta": self.meta.reflection(),
        }

    def __repr__(self) -> str:
        return str(to_dict(self))
