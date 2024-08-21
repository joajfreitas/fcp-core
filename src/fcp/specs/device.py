from typing import *
import datetime
from serde import Model, fields

from . import cmd
from . import config
from . import metadata

from . import v1


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
    commands: fields.List(cmd.Command)
    configs: fields.List(config.Config)
    meta: fields.Optional(metadata.MetaData)

    def get_name(self):
        return self.name

    def get_type(self):
        return "device"

    def to_fpi(self):
        return (
            self.name,
            f"device {self.name} : id({self.id}) {{\n\t"
            + "\n".join([cmd.to_fpi() for cmd in self.commands])
            + "\n"
            + "\n".join([cfg.to_fpi() for cfg in self.configs])
            + "};",
        )

    def to_v1(self):
        return v1.Device(
            msgs={},
            cfgs={cfg.name: cfg.to_v1() for cfg in self.configs},
            cmds={cmd.name: cmd.to_v1() for cmd in self.commands},
            name=self.name,
            id=self.id,
        )

    def __repr__(self):
        return f"<Device name={self.name} id={self.id}"
