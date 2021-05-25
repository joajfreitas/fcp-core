from typing import *
import datetime

from .node import Node

class EnumValue(Node):
    """Fcp EnumValue. C lookalike for FCP type definitions with name-value
    associations.
    """

    def __init__(self, parent: "Enum" = None) -> None:
        self.parent = parent

        assert self.parent is not None

        c = max([value.value for value in self.parent.enumeration.values()] + [0]) + 1
        self._name = ""
        self._value = c

        self.creation_date = datetime.datetime.now()

    def compile(self) -> Dict[str, Any]:
        d = make_public(self, filter_private(self.__dict__))
        return d

    def decompile(self, d: Dict[str, Any]) -> None:
        """Transform node dictionary representation into a python class.

        :param d: Node dictionary
        """

        for k,v in self.make_private(self, d).items():
            self.__setattr__(k,v)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        self._value = int(value)

    def __hash__(self):
        return hash((self._name, self.creation_date))

    def __repr__(self):
        return "name: {}".format(self.name)
