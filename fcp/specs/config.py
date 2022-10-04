import logging
from typing import *
import datetime
from serde import Model, fields
from .metadata import MetaData
from .comment import Comment


class Config(Model):
    """Config node. Represents a Config.

    :param name: Name of the Config.
    :param id: Config identifier.
    :param comment: description of the Config.
    """

    name: fields.Str()
    id: fields.Int()
    type: fields.Str(default="unsigned")
    device: fields.Str()
    comment: Comment
    meta: fields.Optional(MetaData)

    def get_name(self):
        return self.name

    def to_fpi(self):
        logging.info(self.device)

        def show(value, default, fmt):
            if value == default:
                return ""
            else:
                return fmt.format((value))

        output = show(self.comment.value, "", "\t/*{}*/\n")
        output += f"\tconfig {self.name} {{\n"
        output += f"\t\tdevice : {self.device};\n"
        output += f"\t\tid : {self.id};\n"
        output += f"\t\ttype : {self.type};\n"

        return output + "\t};\n"

    def __repr__(self):
        return f"<Config name={self.name}>"
