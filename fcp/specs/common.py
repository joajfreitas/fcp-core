from typing import *
import datetime

from .node import Node, Transmit
from .message import Message
from .config import Config
from .cmd import Command


class Common(Node):
    def __init__(
        self,
        parent: "Spec" = None,
        name: str = "common",
        id: int = 0,
        msgs: Dict[str, Message] = None,
        cfgs: Dict[str, Config] = None,
        cmds: Dict[str, Command] = None,
    ):
        self.parent = parent
        self._name = name
        self._id = id
        self.msgs = {} if msgs is None else msgs
        self.cfgs = {} if cfgs is None else cfgs
        self.cmds = {} if cmds is None else cmds

        self.creation_date = datetime.datetime.now()

    @property
    def name(self) -> str:
        return self._name

    @property
    def id(self) -> int:
        return self._id

    @name.setter
    def name(self, name: str) -> None:
        try:
            self._name = name
        except Exception as e:
            return

    @id.setter
    def id(self, id: int) -> None:
        try:
            self._id = int(id)
        except Exception as e:
            return

    def add_msg(self, msg: Message) -> bool:
        if msg == None:
            return False

        if msg.name in self.msgs.keys():
            return False

        self.msgs[msg.name] = msg
        return True

    def get_msg(self, name: str) -> Message:
        for msg_name, msg in self.msgs.items():
            if msg_name == name:
                return msg

    def __hash__(self):
        return hash((self.name, self.id, self.creation_date))

    def __repr__(self):
        return f"<Common name={self.name} id={self.id}>"
