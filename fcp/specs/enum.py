from typing import *
import datetime
from serde import Model, fields

from .node import Node
from .enum_value import EnumValue


class Enum(Model):
    """Fcp Enum. C lookalike for FCP type definitions with name-value
    associations.
    """

    name: fields.Str()
    enumeration: fields.Dict(fields.Str(), fields.Int())

    def get_name(self):
        return self.name

    def get_type(self):
        return "enum"

    def __repr__(self):
        return "name: {}".format(self.name)
