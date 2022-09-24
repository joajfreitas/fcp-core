from typing import *
import datetime
from serde import Model, fields

from .cmd import Command
from .config import Config
from .utils import normalize
from .metadata import MetaData


class Device(Model):
    """Device node, Represents a CAN device.

    :param name: Name of the Device.
    :param id: FST Device identifier, lowest 5 bits of the identifier.
    :param msgs: Dictionary containing the Device messages.
    :param cmds: Dictionary containing the Device commands.
    :param cfgs: Dictionary containing the Device configs.
    isn't automatically sent.
    """

    name: fields.Str()
    id: fields.Int()
    meta: fields.Optional(MetaData)

    def get_name(self):
        return self.name

    def get_type(self):
        return "device"

    def to_fpi(self):
        return f"device {self.name} {{\n\tid: {self.id};\n}}"

    def __repr__(self):
        return f"<Device name={self.name} id={self.id}"
