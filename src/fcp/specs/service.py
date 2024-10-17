from beartype.typing import List
from serde import serde, strict, to_dict, field

from .rpc import Rpc
from .metadata import MetaData


@serde(type_check=strict)
class Service:
    """Service AST node."""

    name: str
    rpcs: List[Rpc]
    meta: MetaData = field(skip=True)

    def __repr__(self) -> str:
        return str(to_dict(self))
