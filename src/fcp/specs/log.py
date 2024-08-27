from typing import Any, Optional
from serde import serde, strict

from .metadata import MetaData
from .comment import Comment


@serde(type_check=strict)
class Log:
    id: int
    name: str
    comment: Comment
    string: str
    n_args: Optional[int]
    meta: Optional[MetaData]

    def get_name(self) -> str:
        return self.name

    def get_type(self) -> str:
        return "log"

    def to_fpi(self) -> tuple[str, str]:
        def show(value: Any, default: Any, fmt: Any) -> str:
            if value == default:
                return ""
            else:
                return fmt.format((value))

        output = show(self.comment.value, "", "/*{}*/\n")
        output += f"log {self.name} : "
        output += f"id({self.id}) | "
        output += f'str("{self.string}")'
        output += show(self.n_args or 0, 0, " | n_args({})")
        return ("log", output + ";")

    def __repr__(self) -> str:
        return f"<Log name={self.name}>"
