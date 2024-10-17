from serde import serde, strict, to_dict, field

from .metadata import MetaData


@serde(type_check=strict)
class Rpc:
    """Rpc AST node."""

    name: str
    input: str
    output: str
    meta: MetaData = field(skip=True)

    def __repr__(self) -> str:
        return str(to_dict(self))
