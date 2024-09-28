from beartype.typing import Any
from enum import Enum

from .maybe import Maybe, Nothing
from .colors import Color


class Level(Enum):
    Debug = 0
    Info = 1
    Warn = 2
    Error = 3


class FcpError:
    def __init__(
        self, msg: str, level: Level = Level.Error, node: Maybe[Any] = Nothing()
    ):
        self.msg = msg
        self.level = level
        self.node = node

    def __repr__(self):
        return self.msg
