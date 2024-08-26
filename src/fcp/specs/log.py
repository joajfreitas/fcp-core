from typing import Any
from serde import Model, fields

from .metadata import MetaData
from .comment import Comment


class Log(Model):
    id: fields.Int()
    name: fields.Str()
    comment: Comment
    string: fields.Str()
    n_args: fields.Optional(fields.Int())
    meta: fields.Optional(MetaData)

    def get_name(self) -> fields.Str():
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
