from typing import *
import datetime

from .node import Node, Transmit
from ..can import CANMessage

class Config(Transmit):
    """Config node. Represents a Config.

    :param name: Name of the Config.
    :param id: Config identifier.
    :param comment: description of the Config.
    """

    def __init__(
        self,
        parent: "Device" = None,
        name: str = "",
        id: int = 0,
        comment: str = "",
        type: str = "unsigned",
    ):
        self.parent = parent
        self._name = name
        self._id = int(id)
        self._comment = comment
        self._type = type

        self.creation_date = datetime.datetime.now()

    @property
    def name(self) -> str:
        return self._name
 
    @property
    def id(self) -> int:
        return int(self._id)

    @property
    def comment(self) -> str:
        return self._comment

    @property
    def type(self) -> str:
        return self._type

    @name.setter
    def name(self, name: str) -> None:
        try:
            self._name = name
        except Exception as e:
            return

    @id.setter
    def id(self, id: int) -> None:
        try:
            self.id = int(id)
        except Exception as e:
            return

    @comment.setter
    def comment(self, comment: str) -> None:
        try:
            self.comment = comment
        except Exception as e:
            return

    @type.setter
    def type(self, type: str) -> None:
        self.type = type

    def compile(self) -> Dict[str, Any]:
        """Transform python class node to its dictionary representation.

        :return: A dictionary containing the node parameters
        """

        return self.make_public(self, self.filter_private(self.__dict__))

    def decompile(self, d: Dict[str, Any]) -> None:
        """Transform node dictionary representation into a python class.

        :param d: Node dictionary
        """
        #self.__dict__.update(make_private(self, d))
        for k,v in self.make_private(self, d).items():
            self.__setattr__(k,v)

    def normalize(self):
        return

    def encode_set(self, src: int, dst: int, value: int) -> CANMessage:
        common = self.parent.parent.get_common()
        req_set = common.get_msg("req_set")
        msg = req_set.encode({
            "id": self.id,
            "dst": dst,
            "data": value
        })

        return msg

    def encode_get(self, src: int, dst: int) -> CANMessage:
        common = self.parent.parent.get_common()
        req_set = common.get_msg("req_get")
        msg = req_set.encode({
            "id": self.id,
            "dst": dst,
        })

        return msg

    def __hash__(self):
        return hash((self.name, self.id, self.creation_date))
