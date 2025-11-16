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

"""fcp version 2 AST."""

from beartype.typing import Any, Callable, Union, List, Dict, Generator
import serde
import re

from ..xpath import Xpath
from ..maybe import Maybe, Some, Nothing
from ..result import Result, Ok, Err
from .enum import Enum
from .struct_field import StructField
from .struct import Struct
from .impl import Impl
from .service import Service
from .device import Device
from .type import Type, StructType, EnumType


def _flatten(xss: List[List[Any]]) -> List[Any]:
    return [x for xs in xss for x in xs]


def encode_version(version: str) -> int:
    """Encode version string to an integer."""
    major, minor = version.split(".")
    return int(major) * 1000 + int(minor)


@serde.serde(type_check=serde.strict)
class FcpV2:
    """The fcp version 2 AST."""

    structs: List[Struct] = serde.field(default_factory=list)
    enums: List[Enum] = serde.field(default_factory=list)
    impls: List[Impl] = serde.field(default_factory=list)
    services: List[Service] = serde.field(default_factory=list)
    devices: List[Device] = serde.field(default_factory=list)
    version: str = "3.0"

    def merge(self, fcp: "FcpV2") -> None:
        """Merge two fcp ASTs."""
        self.structs += fcp.structs
        self.enums += fcp.enums
        self.impls += fcp.impls

    def get_type(self, type: Type) -> Maybe[Union[Enum, Struct]]:
        """Get node corresponding to type."""
        for type_ in self.structs + self.enums:
            if (
                isinstance(type, StructType) or isinstance(type, EnumType)
            ) and type.name == type_.name:
                return Some(type_)

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
        elif category == "service":
            return Some(self.services)
        elif category == "device":
            return Some(self.devices)
        else:
            return Nothing()

    def get_matching_impl(self, struct: Struct, protocol: str) -> List[Impl]:
        """Get impl for corresponding struct with a specific protocol."""
        impls = []
        for extension in self.impls:
            if extension.type == struct.name and extension.protocol == protocol:
                impls.append(extension)

        return impls

    def get_matching_impls(self, protocol: str) -> Generator[Impl, None, None]:
        """Get impls by protocol name."""
        for impl in self.impls:
            if impl.protocol == protocol:
                yield impl

    def get_matching_impls_or_default(self, protocol: str) -> List[Impl]:
        """Get list of impls matching protocol or the default for a given struct."""
        impls = []
        for struct in self.structs:
            tmp = self.get_matching_impl(struct, protocol)
            if len(tmp) != 0:
                impls += tmp
            else:
                impls += self.get_matching_impl(struct, "default")

        return impls

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

    def get_xpath(self, xpath: Xpath) -> Result[StructField, str]:
        """Get struct field by xpath."""
        if not re.match(r"(\w+):((\w+\/)*\w+)", str(xpath)):
            return Err("Invalid xpath format")

        struct = self.get_struct(xpath.root).unwrap()

        for i in range(len(xpath.path) - 1):
            for field in struct.fields:
                if field.name == xpath.path[i]:
                    struct = self.get_type(field.type).unwrap()

        for field in struct.fields:
            if field.name == xpath.path[-1]:
                return Ok(field)
        return Err("Field not found")

    def get_protocols(self) -> List[str]:
        """Get list of unique protocol names."""
        return list(set([impl.protocol for impl in self.impls]))

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

    def reflection(self) -> Dict[str, Any]:
        """Reflection."""
        return {
            "tag": [0x66, 0x63, 0x70],
            "version": encode_version(self.version),
            "structs": [struct.reflection() for struct in self.structs],
            "enums": [enum.reflection() for enum in self.enums],
            "impls": [impl.reflection() for impl in self.impls],
            "services": [service.reflection() for service in self.services],
        }

    def __repr__(self) -> str:
        return str(serde.to_dict(self))
