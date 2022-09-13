from typing import *
import datetime
from serde import Model, fields

from .node import Node
from .enum_value import EnumValue
from .metadata import MetaData


class Enumeration(Model):
    name: fields.Str()
    value: fields.Int()
    meta: fields.Optional(MetaData)


class Enum(Model):
    """Fcp Enum. C lookalike for FCP type definitions with name-value
    associations.
    """

    name: fields.Str()
    enumeration: fields.List(Enumeration)
    meta: fields.Optional(MetaData)

    def get_name(self):
        return self.name

    def get_type(self):
        return "enum"

    def __repr__(self):
        return "name: {}".format(self.name)
