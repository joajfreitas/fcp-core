from serde import serde, strict
from beartype.typing import Union
from typing_extensions import Self


@serde(type_check=strict)
class BuiltinType:
    name: str

    def get_length(self) -> int:
        return int(self.name[1:])

    def is_signed(self) -> bool:
        return self.name[0] == "i"


@serde(type_check=strict)
class ComposedType:
    name: str


@serde(type_check=strict)
class ArrayType:
    type: Union[BuiltinType, ComposedType, Self]
    size: int


Type = Union[BuiltinType, ArrayType, ComposedType]
