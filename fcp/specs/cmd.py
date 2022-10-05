from typing import *
import datetime
from serde import Model, fields

from .arg import Argument
from .metadata import MetaData
from .comment import Comment


class Command(Model):
    name: fields.Str()
    n_args: fields.Optional(fields.Int(default=0))
    id: fields.Int()
    args: fields.List(Argument)
    rets: fields.List(Argument)
    device: fields.Str()
    comment: Comment
    meta: fields.Optional(MetaData)

    def get_name(self):
        return self.name

    def get_type(self):
        return "command"

    def to_fpi(self):
        def show(value, default, fmt):
            if value == default:
                return ""
            else:
                return fmt.format((value))

        output = show(self.comment.value, "", "\t/*{}*/\n")
        output += f"\tcommand {self.name} : "
        output += f"device({self.device}) | "
        output += f"id({self.id})"
        output += show(len(self.args), 0, " | n_args({})")
        output = output + ";"
        return output

        # if len(self.args) == 0 and len(self.rets) == 0:
        # return output + ";\n"

        output += "{\n"
        for arg in self.args:
            output += arg.to_idl() + "\n"

        for ret in self.rets:
            output += ret.to_idl() + "\n"

        return output + "}\n"
