from typing import Optional
from serde import serde, strict

from .metadata import MetaData
from .comment import Comment


@serde(type_check=strict)
class Log:
    id: int
    name: str
    comment: Comment
    string: str
    n_args: Optional[int] = None
    meta: Optional[MetaData] = None

    def get_name(self) -> str:
        return self.name

    def get_type(self) -> str:
        return "log"

    def __repr__(self) -> str:
        return f"<Log name={self.name}>"
