from typing import *
import datetime
from serde import Model, fields

from .metadata import MetaData
from .comment import Comment
from . import v1


class Log(Model):
    id: fields.Int()
    name: fields.Str()
    comment: Comment
    string: fields.Str()
    n_args: fields.Optional(fields.Int())
    meta: fields.Optional(MetaData)

    def get_name(self):
        return self.name

    def get_type(self):
        return "log"

    def to_fpi(self):
        def show(value, default, fmt):
            if value == default:
                return ""
            else:
                return fmt.format((value))

        output = show(self.comment.value, "", "/*{}*/\n")
        output += f"log {self.name} : "
        output += f"id({self.id}) | "
        output += f'str("{self.string}")'
        output += show(self.n_args or 0, 0, " | n_args({})")
        return ("log", output + ";")

    def __repr__(self):
        return f"<Log name={self.name}>"
