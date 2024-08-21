from typing import *
import datetime
from serde import Model, fields
import logging

from .metadata import MetaData
from .comment import Comment
from . import v1


class CommandArg(Model):
    name: fields.Str()
    id: fields.Int()
    type: fields.Str()
    comment: fields.Optional(Comment)

    def to_fpi(self):
        return f"\t\t/*{self.comment.value}*/\n\t\targ {self.name} @{self.id}: {self.type};"


class CommandRet(Model):
    name: fields.Str()
    id: fields.Int()
    type: fields.Str()
    comment: fields.Optional(Comment)

    def to_fpi(self):
        return f"\t\t/*{self.comment.value}*/\n\t\tret {self.name} @{self.id}: {self.type};"


class Command(Model):
    name: fields.Str()
    id: fields.Int()
    args: fields.List(CommandArg)
    rets: fields.List(CommandRet)
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
        if len(self.args) + len(self.rets) == 0:
            output = output + ";"
            return output
        else:
            output += " {\n"
            for arg in self.args:
                output += arg.to_fpi() + "\n"

            for ret in self.rets:
                output += ret.to_fpi() + "\n"
            output += "\t};"
            return output
