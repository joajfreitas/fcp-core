import sys

from typing import Optional, Any
from serde import serde, strict
from .metadata import MetaData
from .comment import Comment


@serde(type_check=strict)
class Config:
    """Config node. Represents a Config.

    :param name: Name of the Config.
    :param id: Config identifier.
    :param comment: description of the Config.
    """

    name: str
    id: int
    device: str
    comment: Comment
    meta: Optional[MetaData]
    type: str = "unsigned"

    def get_name(self) -> str:
        return self.name

    def to_fpi(self) -> str:
        def show(value: Any, default: Any, fmt: Any) -> str:
            if value == default:
                return ""
            else:
                return str(fmt.format((value)))

        if self.type == "unsigned":
            type = "u32"
        else:
            sys.exit(1)

        output = show(self.comment.value, "", "\t/*{}*/\n")
        output += f"\tconfig {self.name} : "
        output += f"{type} | "
        output += f"device({self.device}) | "
        output += f"id({self.id})"

        return output + ";"

    def __repr__(self) -> str:
        return f"<Config name={self.name}>"
