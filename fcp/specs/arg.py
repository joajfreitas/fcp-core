from typing import *
import datetime

from .node import Node

class Argument(Node):
    """Argument node. Represents a Command Argument.

    :param name: Name of the Argument.
    :param id: Argument identifier.
    :param comment: description of the Argument.
    """

    def __init__(
        self,
        parent: "Command" = None,
        name: str = "",
        id: int = 0,
        comment: str = "",
        type: str = "unsigned",
    ):
        self.parent = parent
        self._name = name
        self._id = id
        self._comment = comment
        self._type = type

        self.creation_date = datetime.datetime.now()

    @property
    def name(self) -> str:
        return self._name

    @property
    def comment(self) -> str:
        return self._comment

    @property
    def id(self) -> int:
        return self._id

    @property
    def type(self) -> str:
        return self._type

    @name.setter
    def name(self, name: str) -> None:
        try:
            self._name = name
        except Exception as e:
            return

    @comment.setter
    def comment(self, comment: str) -> None:
        try:
            self._comment = comment
        except Exception as e:
            return

    @id.setter
    def id(self, id: int) -> None:
        try:
            self._id = int(id)
        except Exception as e:
            return

    @type.setter
    def type(self, type: str) -> None:
        self._type = type

    def compile(self) -> Dict[str, Any]:
        """Transform python class node to its dictionary representation.

        :return: A dictionary containing the node parameters
        """
        d = self.make_public(self, self.filter_private(self.__dict__))
        return d

    def decompile(self, d: Dict[str, Any]) -> None:
        """Transform node dictionary representation into a python class.

        :param d: Node dictionary
        """
        #self.__dict__.update(make_private(self, d))
        for k,v in self.make_private(self,d).items():
            self.__setattr__(k,v)
