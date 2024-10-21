from beartype.typing import Any
from enum import Enum


class Level(Enum):
    """Log level."""

    Debug = 0
    Info = 1
    Warn = 2
    Error = 3


class FcpError:
    """Fcp error."""

    def __init__(self, msg: str, node: Any, level: Level = Level.Error):
        self.msg = msg
        self.level = level
        self.node = node

    def __repr__(self) -> str:
        return self.msg
