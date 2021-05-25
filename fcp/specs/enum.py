from typing import *
import datetime

from .node import Node
from .utils import normalize
from .enum_value import EnumValue

class Enum(Node):
    """Fcp Enum. C lookalike for FCP type definitions with name-value
    associations.
    """

    def __init__(self, parent: "Spec" = None) -> None:
        self.parent = parent
        self._name = ""
        self.enumeration = {}
        self.creation_date = datetime.datetime.now()

    def compile(self) -> Dict[str, Any]:
        enums = {k: v.compile() for (k, v) in self.enumeration.items()}

        d = make_public(self, (filter_private(self.__dict__)))
        d["enumeration"] = enums
        return d

    def decompile(self, d: Dict[str, Any]) -> None:
        """Transform node dictionary representation into a python class.

        :param d: Node dictionary
        """
        enumeration = d["enumeration"]
        del d["enumeration"]

        #self.__dict__.update(make_private(self, d))
        for k,v in self.make_private(self, d).items():
            self.__setattr__(k,v)

        for k, v in enumeration.items():
            enum_value = EnumValue(self)
            enum_value.decompile(v)
            self.enumeration[k] = enum_value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self.name = name

    def normalize(self):
        normalize(self.enumeration)

    def __hash__(self):
        return hash((self.name, self.creation_date))

    def __repr__(self):
        return "name: {}".format(self.name)

