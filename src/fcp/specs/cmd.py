from serde import serde, strict
from typing import Any, Optional

from .metadata import MetaData
from .comment import Comment


@serde(type_check=strict)
class CommandArg:
    name: str
    id: int
    type: str
    comment: Optional[Comment]

    def to_fpi(self) -> str:
        comment = self.comment.value if self.comment is not None else ""
        return f"\t\t/*{comment}*/\n\t\targ {self.name} @{self.id}: {self.type};"


@serde(type_check=strict)
class CommandRet:
    name: str
    id: int
    type: str
    comment: Optional[Comment]

    def to_fpi(self) -> str:
        comment = self.comment.value if self.comment is not None else ""
        return f"\t\t/*{comment}*/\n\t\tret {self.name} @{self.id}: {self.type};"


@serde(type_check=strict)
class Command:
    name: str
    id: int
    args: list[CommandArg]
    rets: list[CommandRet]
    device: str
    comment: Comment
    meta: Optional[MetaData]

    def get_name(self) -> str:
        return self.name

    def get_type(self) -> str:
        return "command"

    def to_fpi(self) -> str:
        def show(value: Any, default: Any, fmt: Any) -> str:
            if value == default:
                return ""
            else:
                return str(fmt.format((value)))

        output = show(self.comment.value, "", "\t/*{}*/\n")
        output += f"\tcommand {self.name} : "
        output += f"device({self.device}) | "
        output += f"id({self.id})"
        if len(self.args) + len(self.rets) == 0:
            output = output + ";"
            return output
        else:
            output += " {\n"
            for arg in self.args:
                output += arg.to_fpi() + "\n"

            for ret in self.rets:
                output += ret.to_fpi() + "\n"
            output += "\t};"
            return output
