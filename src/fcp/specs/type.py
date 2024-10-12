from serde import serde, strict
from beartype.typing import Union, Self


@serde(type_check=strict)
class BuiltinType:
    name: str

    def get_length(self) -> int:
        return int(self.name[1:])

    def is_signed(self) -> bool:
        return self.name[0] == "i"


@serde(type_check=strict)
class CompoundType:
    name: str


@serde(type_check=strict)
class ArrayType:
    type: Union[BuiltinType, CompoundType, Self]
    size: int


Type = Union[BuiltinType, ArrayType, CompoundType]
