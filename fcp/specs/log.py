from typing import *
import datetime

from .node import Node

class Log(Node):
    """Log protocol node.

    :param id: Log integer identifier.
    :param name: Name of the Log node.
    :param n_args: Number of arguments in the Log node.
    :param comment: Description of the Log node
    :param string: Display string for the Log node.
    """

    def __init__(
        self,
        parent: "Spec" = None,
        id: int = 0,
        name: str = "",
        n_args: int = 3,
        comment: str = "",
        string: str = "",
    ):
        self.parent = parent
        assert self.parent is not None

        c = max([log.id for log in self.parent.logs.values()] + [0]) + 1
        self._id = id or c
        self._name = name
        self._n_args = n_args
        self._comment = comment
        self._string = string

        self.creation_date = datetime.datetime.now()

    def compile(self) -> Dict[str, Any]:
        """Transform python class node to its dictionary representation.

        :return: A dictionary containing the node parameters
        """
        return self.make_public(self, self.filter_private(self.__dict__))

    def decompile(self, d: Dict[str, Any]) -> None:
        """Transform node dictionary representation into a python class.

        :param d: Node dictionary
        """
        for k, v in self.make_private(self, d).items():
            self.__setattr__(k, v)

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def n_args(self) -> int:
        return self._n_args

    @property
    def comment(self) -> str:
        return self._comment

    @property
    def string(self) -> str:
        return self._string

    @id.setter
    def id(self, id: int) -> None:
        try:
            self._id = int(id)
        except Exception as e:
            return

    @name.setter
    def name(self, name: str) -> None:
        try:
            self._name = name
        except Exception as e:
            return

    @n_args.setter
    def n_args(self, n_args: int) -> None:
        try:
            self._n_args = int(n_args)
        except Exception as e:
            return

    @comment.setter
    def comment(self, comment: str) -> None:
        try:
            self._comment = comment
        except Exception as e:
            return

    @string.setter
    def string(self, string: str) -> None:
        try:
            self._string = string
        except Exception as e:
            return

    def __hash__(self):
        return hash((self.name, self.id, self.creation_date))

    def __repr__(self):
        return f"<Log name: {self.name}, id: {self.id}, n_args: {self.n_args}>"
