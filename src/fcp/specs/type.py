from serde import serde, strict
from beartype.typing import Union
from typing_extensions import Self


@serde(type_check=strict)
class BuiltinType:
    """fcp builtin types."""

    name: str

    def get_length(self) -> int:
        """Check type length in bits."""
        return int(self.name[1:])

    def is_signed(self) -> bool:
        """Check that type is signed."""
        return self.name[0] == "i"


@serde(type_check=strict)
class ComposedType:
    """fcp type for user defined types such as structs and enums."""

    name: str


@serde(type_check=strict)
class ArrayType:
    """fcp array type."""

    type: Union[BuiltinType, ComposedType, Self]
    size: int


Type = Union[BuiltinType, ArrayType, ComposedType]
