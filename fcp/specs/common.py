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


    def compile(self) -> Dict[str, Any]:
        """Transform python class node to its dictionary representation.

        :return: A dictionary containing the node parameters
        """

        msgs = {}
        for msg_k, msg_v in self.msgs.items():
            msgs[msg_k] = msg_v.compile()

        att = self.make_public(self, self.filter_private(self.__dict__))
        att["msgs"] = msgs
        return att

    def decompile(self, d: Dict[str, Any]) -> None:
        """Transform node dictionary representation into a python class.

        :param d: Node dictionary
        """
        msgs = d["msgs"]
        del d["msgs"]

        self.__dict__.update(self.make_private(self, d))

        for key, value in msgs.items():
            msg = Message(self)
            msg.decompile(value)
            self.msgs[key] = msg

    def __hash__(self):
        return hash((self.name, self.id, self.creation_date))

    def __repr__(self):
        return f"<Common name={self.name} id={self.id}>"
