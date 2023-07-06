import math
from typing import *
import datetime
from serde import Model, fields

from .metadata import MetaData
from .comment import Comment


class Enumeration(Model):
    name: fields.Str()
    value: fields.Int()
    meta: fields.Optional(MetaData)

    def to_dict(self):
        return {"name": self.name, "value": self.value}


class Enum(Model):
    """Fcp Enum. C lookalike for FCP type definitions with name-value
    associations.
    """

    name: fields.Str()
    enumeration: fields.List(Enumeration)
    meta: fields.Optional(MetaData)
    comment: fields.Optional(Comment)

    def get_name(self):
        return self.name

    def get_type(self):
        return "enum"

    def get_size(self):
        return math.floor(math.log2(max([enum.value for enum in self.enumeration]))) + 1

    def to_fcp(self):
        return (
            "enum",
            (f"/*{self.comment.value}*/\n" if self.comment.value != "" else "")
            + f"enum {self.name} {{\n\t"
            + "\n\t".join([f"{enum.name}: {enum.value};" for enum in self.enumeration])
            + "\n};",
        )

    def to_dict(self):
        return {
            "name": self.name,
            "enumeration": [enumeration.to_dict() for enumeration in self.enumeration],
            }

    def to_dict(self):
        return {}

    def __repr__(self):
        return "name: {}".format(self.name)
