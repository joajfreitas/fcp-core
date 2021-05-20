from typing import *
import datetime

from .node import Node
from .message import Message
from .cmd import Command
from .config import Config
from .utils import normalize

class Device(Node):
    """Device node, Represents a CAN device.

    :param name: Name of the Device.
    :param id: FST Device identifier, lowest 5 bits of the identifier.
    :param msgs: Dictionary containing the Device messages.
    :param cmds: Dictionary containing the Device commands.
    :param cfgs: Dictionary containing the Device configs.
    isn't automatically sent.
    """

    def __init__(
        self,
        parent: "Spec" = None,
        name: str = "",
        id: int = 0,
        msgs: Dict[str, Message] = None,
        cmds: Dict[str, Command] = None,
        cfgs: Dict[str, Config] = None,
    ):

        self.parent = parent
        assert self.parent is not None
        c = max([dev.id for dev in self.parent.devices.values()] + [0]) + 1

        self._name = name or ("device" + str(c))
        self._id = id or c
        self.msgs = {} if msgs == None else msgs
        self.cmds = {} if cmds == None else cmds
        self.cfgs = {} if cfgs == None else cfgs

        self.creation_date = datetime.datetime.now()

    @property
    def name(self) -> str:
        return self._name

    @property
    def id(self) -> int:
        return self._id

    @name.setter
    def name(self, name: str) -> None:
        try:
            self._name = name
        except Exception as e:
            return

    @id.setter
    def id(self, id: int) -> None:
        print("set id")
        try:
            self._id = int(id)
        except Exception as e:
            return


    def add_cmd(self, cmd: Command) -> None:
        self.cmds[cmd.name] = cmd

    def add_cfg(self, cfg: Config) -> None:
        self.cfgs[cfg.name] = cfg

    def compile(self) -> Dict[str, Any]:
        """Transform python class node to its dictionary representation.

        :return: A dictionary containing the node parameters
        """

        msgs = {}
        cmds = {}
        cfgs = {}

        for msg_k, msg_v in self.msgs.items():
            msgs[msg_k] = msg_v.compile()

        for cmd_k, cmd_v in self.cmds.items():
            cmds[cmd_k] = cmd_v.compile()

        for cfg_k, cfg_v in self.cfgs.items():
            cfgs[cfg_k] = cfg_v.compile()

        att = self.make_public(self, self.filter_private(self.__dict__))
        att["msgs"] = msgs
        att["cmds"] = cmds
        att["cfgs"] = cfgs

        return att

    def decompile(self, d: Dict[str, Any]) -> None:
        """Transform node dictionary representation into a python class.

        :param d: Node dictionary
        """

        msgs = d["msgs"]
        cmds = d["cmds"]
        cfgs = d["cfgs"]

        for k, v in self.make_private(self, d).items():
            f = self.__setattr__(k, v)

        #self.__dict__.update()

        for k, v in msgs.items():
            msg = Message(self)
            msg.decompile(v)
            self.msgs[k] = msg

        for k, v in cmds.items():
            cmd = Command(self)
            cmd.decompile(v)
            self.cmds[k] = cmd

        for k, v in cfgs.items():
            cfg = Config(self)
            cfg.decompile(v)
            self.cfgs[k] = cfg

    def add_msg(self, msg: Message) -> bool:
        """Add a Message to Device.

        :param msg: Message to be added.
        :return: Operation success status: True - Success, False - Failure
        """
        if msg == None:
            return False

        if msg.name in self.msgs.keys():
            return False

        self.msgs[msg.name] = msg

        return True

    def get_msg(self, name: str) -> Optional[Message]:
        """Get a Message from Device by its name.

        :param name: Message name.
        :return: Message or None if not found.
        """
        return self.msgs.get(name)

    def rm_msg(self, name: str) -> bool:
        """Remove a Message from Device.

        :param name: Name of the Message to be removed.
        """
        if self.get_msg(name) is None:
            return False

        del self.msgs[name]
        return True

    def rm_cmd(self, name: str) -> bool:
        """Remove a Command from Device.

        :param name: Name of the Command to be removed.
        """
        if self.get_cmd(name) is None:
            return False

        del self.cmds[name]
        return True

    def get_cfg(self, name: str) -> Optional[Config]:
        """Get a Config from Device by its name.

        :param name: Config name.
        :return: Config or None if not found.
        """

        if type(name) is str:
            return self.cfgs.get(name)
        if type(name) is int or type(name) is float:
            for cfg in self.cfgs.values():
                if cfg.id == int(name):
                    return cfg

    def rm_cfg(self, name: str) -> bool:
        """Remove a Config from Device.

        :param name: Name of the Config to be removed.
        """
        if self.get_cfg(name) is None:
            return False

        del self.cfgs[name]
        return True

    def normalize(self):
        """ Update messages, commands and configs dictionary keys.  """
        normalize(self.msgs)
        normalize(self.cmds)
        normalize(self.cfgs)

        for key, msg in self.msgs.items():
            msg.normalize()

        for key, cmd in self.cmds.items():
            cmd.normalize()

        for key, cfg in self.cfgs.items():
            cfg.normalize()

    def get_cmd(self, name: Union[str, int]) -> Optional[Command]:
        if type(name) is str:
            return self.cmds.get(name)
        if type(name) is int or type(name) is float:
            for cmd in self.cmds.values():
                if cmd.id == int(name):
                    return cmd

    def __hash__(self):
        return hash((self.name, self.id, self.creation_date))

    def __repr__(self):
        return f"<Device name={self.name} id={self.id}>"

