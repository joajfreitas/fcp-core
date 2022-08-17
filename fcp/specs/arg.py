from typing import *
import datetime
from serde import Model, fields

from .node import Node


class Argument(Model):
    """Argument node. Represents a Command Argument.

    :param name: Name of the Argument.
    :param id: Argument identifier.
    :param comment: description of the Argument.
    """

    name: fields.Str()
    id: fields.Int()
    comment: fields.Str()
    type: fields.Optional(fields.Str(default="unsigned"))

    def to_idl(self):
        def show(value, default, fmt):
            if value == default:
                return ""
            else:
                return fmt.format((value))

        output = show(self.comment, "", "/*{}*/\n")
        output += f"arg {self.name}: "
        output += f"id({self.id}) | "
        output += show(self.type, "unsigned", "type({}) | ")

        return output[:-3] + ";"

    # @property
    # def name(self) -> str:
    #    return self._name

    # @property
    # def comment(self) -> str:
    #    return self._comment

    # @property
    # def id(self) -> int:
    #    return self._id

    # @property
    # def type(self) -> str:
    #    return self._type

    # @name.setter
    # def name(self, name: str) -> None:
    #    try:
    #        self._name = name
    #    except Exception as e:
    #        return

    # @comment.setter
    # def comment(self, comment: str) -> None:
    #    try:
    #        self._comment = comment
    #    except Exception as e:
    #        return

    # @id.setter
    # def id(self, id: int) -> None:
    #    try:
    #        self._id = int(id)
    #    except Exception as e:
    #        return

    # @type.setter
    # def type(self, type: str) -> None:
    #    self._type = type

    # def compile(self) -> Dict[str, Any]:
    #    """Transform python class node to its dictionary representation.

    #    :return: A dictionary containing the node parameters
    #    """
    #    d = self.make_public(self, self.filter_private(self.__dict__))
    #    return d

    # def decompile(self, d: Dict[str, Any]) -> None:
    #    """Transform node dictionary representation into a python class.

    #    :param d: Node dictionary
    #    """
    #    # self.__dict__.update(make_private(self, d))
    #    for k, v in self.make_private(self, d).items():
    #        self.__setattr__(k, v)
