from typing import *
import datetime
from serde import Model, fields

from .metadata import MetaData
from .comment import Comment


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
    comment: Comment

    def get_name(self):
        return self.name

    def get_type(self):
        return "enum"

    def to_fcp(self):
        return (
            "enum",
            (f"/*{self.comment.value}*/\n" if self.comment.value != "" else "")
            + f"enum {self.name} {{\n\t"
            + "\n\t".join([f"{enum.name}: {enum.value};" for enum in self.enumeration])
            + "\n};",
        )

    def __repr__(self):
        return "name: {}".format(self.name)
