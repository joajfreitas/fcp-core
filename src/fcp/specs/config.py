import sys
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
        def show(value, default, fmt):
            if value == default:
                return ""
            else:
                return fmt.format((value))

        if self.type == "unsigned":
            type = "u32"
        else:
            sys.exit(1)

        output = show(self.comment.value, "", "\t/*{}*/\n")
        output += f"\tconfig {self.name} : "
        output += f"{type} | "
        output += f"device({self.device}) | "
        output += f"id({self.id})"

        return output + ";"

    def __repr__(self):
        return f"<Config name={self.name}>"
