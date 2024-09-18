from typing import Optional
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
    type: str = "unsigned"
    meta: Optional[MetaData] = None

    def get_name(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Config name={self.name}>"
