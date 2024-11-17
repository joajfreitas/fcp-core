"""fcp version 2 AST."""

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

from beartype.typing import Any, Callable, Union, List, Dict, Generator
import serde
import struct

from ..maybe import Maybe, Some, Nothing
from .enum import Enum
from .struct_field import StructField
from .struct import Struct
from .impl import Impl
from .service import Service
from .type import Type, BuiltinType


def _flatten(xss: List[List[Any]]) -> List[Any]:
    return [x for xs in xss for x in xs]


@serde.serde(type_check=serde.strict)
class FcpV2:
    """The fcp version 2 AST."""

    structs: List[Struct] = serde.field(default_factory=list)
    enums: List[Enum] = serde.field(default_factory=list)
    impls: List[Impl] = serde.field(default_factory=list)
    services: List[Service] = serde.field(default_factory=list)
    version: str = "3.0"

    def merge(self, fcp: "FcpV2") -> None:
        """Merge two fcp ASTs."""
        self.structs += fcp.structs
        self.enums += fcp.enums
        self.impls += fcp.impls

    def get_type(self, type: Type) -> Maybe[Union[Enum, Struct]]:
        """Get node corresponding to type."""
        for type_ in self.structs + self.enums:
            if type.name == type_.name:
                return Some(type_)

        if isinstance(type, BuiltinType):
            return Some(type)

        return Nothing()

    def get_types(self) -> List[Any]:
        """Get fcp types. Fcp types are enums and structs."""
        return self.structs + self.enums

    def get(self, category: str) -> Maybe[List[Any]]:
        """Get fcp node by category."""
        if category == "struct":
            return Some(self.structs)
        elif category == "enum":
            return Some(self.enums)
        elif category == "impl":
            return Some(self.impls)
        elif category == "field":
            return Some(
                _flatten(
                    [
                        [(struct, field) for field in struct.fields]
                        for struct in self.structs
                    ]
                )
            )
        elif category == "signal_block":
            return Some(_flatten([extension.signals for extension in self.impls]))
        elif category == "type":
            return Some(self.get_types())
        else:
            return Nothing()

    def get_matching_impl(self, struct: Struct, protocol: str) -> Maybe[Impl]:
        """Get impl for corresponding struct with a specific protocol."""
        for extension in self.impls:
            if extension.type == struct.name and extension.protocol == protocol:
                return Some(extension)

        return Nothing()

    def get_matching_impls(self, protocol: str) -> Generator[Impl, None, None]:
        """Get impls by protocol name."""
        for extension in self.impls:
            if extension.protocol == protocol:
                yield extension

    def get_struct(self, name: str) -> Maybe[Struct]:
        """Get struct by name."""
        for struct in self.structs:
            if struct.name == name:
                return Some(struct)

        return Nothing()

    def get_enum(self, name: str) -> Maybe[Enum]:
        """Get enum by name."""
        for enum in self.enums:
            if enum.name == name:
                return Some(enum)

        return Nothing()

    def to_dict(self) -> Any:
        """Get the fcp AST as a python dictionary."""

        def filter_tree(filter: Callable[[Any, Any], bool]) -> Callable[[Any], Any]:
            def closure(tree: Any) -> Any:
                if isinstance(tree, dict):
                    return {k: closure(v) for k, v in tree.items() if filter(k, v)}
                elif isinstance(tree, list):
                    return [closure(x) for x in tree]
                else:
                    return tree

            return closure

        remove_none_fields = filter_tree(lambda k, v: v is not None)
        remove_meta = filter_tree(lambda k, v: k != "meta")

        return remove_meta(remove_none_fields(serde.to_dict(self)))

    def __repr__(self) -> str:
        return str(serde.to_dict(self))
