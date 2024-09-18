from serde import serde, strict
from typing import Optional

from .metadata import MetaData
from .comment import Comment


@serde(type_check=strict)
class CommandArg:
    name: str
    id: int
    type: str
    comment: Optional[Comment] = None


@serde(type_check=strict)
class CommandRet:
    name: str
    id: int
    type: str
    comment: Optional[Comment] = None


@serde(type_check=strict)
class Command:
    name: str
    id: int
    args: list[CommandArg]
    rets: list[CommandRet]
    device: str
    comment: Comment
    meta: Optional[MetaData] = None

    def get_name(self) -> str:
        return self.name

    def get_type(self) -> str:
        return "command"
