from typing import *
import datetime
from serde import Model, fields

from .metadata import MetaData
from .comment import Comment


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

        output = show(self.comment, "", "/*{}*/\n")
        output += f"log {self.name} {{\n"
        output += f"\tid: {self.id};\n"
        output += f'\tstr: "{self.string}";\n'
        output += show(self.n_args or 0, 0, "\tn_args: {};\n")
        return output + "}"

    def __repr__(self):
        return f"<Log name={self.name}>"
