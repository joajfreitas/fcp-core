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


def handle_key_not_found(d: Dict[str, Any], key: str) -> List[Any]:
    return d.get(key).items() if d.get(key) is not None else []  # type: ignore


def flatten(xss: List[List[Any]]) -> List[Any]:
    return [x for xs in xss for x in xs]


@serde.serde(type_check=serde.strict)
class FcpV2:
    """FCP root node. Holds all Signals, Configs,
    Commands and Arguments.
    """

    structs: List[Struct] = serde.field(default_factory=list)
    enums: List[Enum] = serde.field(default_factory=list)
    impls: List[Impl] = serde.field(default_factory=list)
    services: List[Service] = serde.field(default_factory=list)
    version: str = "3.0"

    def merge(self, fcp: "FcpV2") -> None:
        self.structs += fcp.structs
        self.enums += fcp.enums
        self.impls += fcp.impls

    def get_type(self, type: Type) -> Maybe[Union[Enum, Struct]]:
        for type_ in self.structs + self.enums:
            if type.name == type_.name:
                return Some(type_)

        if isinstance(type, BuiltinType):
            return Some(type)

        return Nothing()

    def get_types(self) -> List[Any]:
        return self.structs + self.enums

    def get(self, category: str) -> Maybe[List[Any]]:
        if category == "struct":
            return Some(self.structs)
        elif category == "enum":
            return Some(self.enums)
        elif category == "impl":
            return Some(self.impls)
        elif category == "field":
            return Some(
                flatten(
                    [
                        [(struct, field) for field in struct.fields]
                        for struct in self.structs
                    ]
                )
            )
        elif category == "signal_block":
            return Some(flatten([extension.signals for extension in self.impls]))
        elif category == "type":
            return Some(self.get_types())
        else:
            return Nothing()

    def get_matching_extension(self, struct: Struct, protocol: str) -> Maybe[Impl]:
        for extension in self.impls:
            if extension.type == struct.name and extension.protocol == protocol:
                return Some(extension)

        return Nothing()

    def get_matching_impls(self, protocol: str) -> Generator[Impl, None, None]:
        for extension in self.impls:
            if extension.protocol == protocol:
                yield extension

    def get_struct(self, name: str) -> Maybe[Struct]:
        for struct in self.structs:
            if struct.name == name:
                return Some(struct)

        return Nothing()

    def to_fcp(self) -> Dict[str, List[Dict[str, Any]]]:
        nodes = [node.to_fcp() for node in self.enums + self.structs]
        fcp_structure: Dict[str, List[Any]] = {}

        for node in nodes:
            if node[0] not in fcp_structure.keys():
                fcp_structure[node[0]] = []
            fcp_structure[node[0]].append(node[1])

        return fcp_structure

    def to_dict(self) -> Any:
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


def default_serialization(fcp: FcpV2, typename: str, data: Dict[str, Any]) -> bytearray:
    """
    ```fcp
    struct foo {
        var1: u8;
        var2: u16;
    };

    struct bar {
        var1: foo;
        var2: f32;
    };
    ```

    data:

    {
        "var1":
            {
                "var1": 4,
                "var2": 257
            },
        "var2": 10.1
    }

    [4, 1, 1, 65, 33, 153, 154]
    """

    structs = {struct.name: struct for struct in fcp.structs}

    def serialize_signal(
        field: StructField, value: Union[Dict["str", Any], Any]
    ) -> Any:
        conversions: Dict[str, Callable[[Any], bytearray]] = {
            "u8": lambda x: x.to_bytes(1, signed=False, byteorder="little"),
            "u16": lambda x: x.to_bytes(2, signed=False, byteorder="little"),
            "u32": lambda x: x.to_bytes(4, signed=False, byteorder="little"),
            "u64": lambda x: x.to_bytes(8, signed=False, byteorder="little"),
            "i8": lambda x: x.to_bytes(1, signed=True, byteorder="little"),
            "i16": lambda x: x.to_bytes(2, signed=True, byteorder="little"),
            "i32": lambda x: x.to_bytes(4, signed=True, byteorder="little"),
            "i64": lambda x: x.to_bytes(8, signed=True, byteorder="little"),
            "f32": lambda x: bytearray(struct.pack("f", x)),
            "f64": lambda x: bytearray(struct.pack("d", x)),
        }

        if isinstance(field.type, BuiltinType):
            return conversions[field.type.name](value)
        elif field.type is not None:
            return serialize_struct(structs[field.type.name], value)
        else:
            raise ValueError()

    def serialize_struct(struct: Struct, data: Dict["str", Any]) -> bytearray:
        buffer = bytearray()
        for signal in struct.fields:
            buffer += serialize_signal(signal, data[signal.name])

        return buffer

    return serialize_struct(structs[typename], data)
