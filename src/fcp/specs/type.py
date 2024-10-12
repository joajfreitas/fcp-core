from serde import serde, strict
from beartype.typing import Union


@serde(type_check=strict)
class DefaultType:
    name: str

    def get_length(self) -> int:
        return int(self.name[1:])

    def is_signed(self) -> bool:
        return self.name[0] == "i"


@serde(type_check=strict)
class ArrayType:
    name: str
    size: int


@serde(type_check=strict)
class CompoundType:
    name: str


Type = Union[DefaultType, ArrayType, CompoundType]
