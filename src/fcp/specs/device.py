from serde import serde, strict
from typing import Optional

from . import cmd
from . import config
from . import metadata


@serde(type_check=strict)
class Device:
    """Device node, Represents a CAN device.

    :param name: Name of the Device.
    :param id: FST Device identifier, lowest 5 bits of the identifier.
    :param msgs: Dictionary containing the Device messages.
    :param cmds: Dictionary containing the Device commands.
    :param cfgs: Dictionary containing the Device configs.
    isn't automatically sent.
    """

    name: str
    id: int
    commands: list[cmd.Command]
    configs: list[config.Config]
    meta: Optional[metadata.MetaData] = None

    def get_name(self) -> str:
        return self.name

    def get_type(self) -> str:
        return "device"

    def __repr__(self) -> str:
        return f"<Device name={self.name} id={self.id}"
