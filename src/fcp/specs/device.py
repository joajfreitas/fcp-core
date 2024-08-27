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
    meta: Optional[metadata.MetaData]

    def get_name(self) -> str:
        return self.name

    def get_type(self) -> str:
        return "device"

    def to_fpi(self) -> tuple[str, str]:
        return (
            self.name,
            f"device {self.name} : id({self.id}) {{\n\t"
            + "\n".join([cmd.to_fpi() for cmd in self.commands])
            + "\n"
            + "\n".join([cfg.to_fpi() for cfg in self.configs])
            + "};",
        )

    def __repr__(self) -> str:
        return f"<Device name={self.name} id={self.id}"
