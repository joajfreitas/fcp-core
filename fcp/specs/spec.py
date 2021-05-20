from typing import *
import copy
import datetime
import time

from . import *
from .utils import normalize


def handle_key_not_found(d: dict, key: str):
    return d.get(key).items() if d.get(key) != None else []

class Spec:
    """FCP root node. Holds all Devices, Messages, Signals, Logs, Configs,
    Commands and Arguments.
    """

    def __init__(self) -> None:
        self.devices = {}
        self.common = Common()
        self.logs = {}
        self.enums = {}
        self.version = "0.2"
        self.parent = None
        self.name = ""

    def add_device(self, device: "Device") -> bool:
        """Add a Device to Spec.

        :param device: Device to be added
        :return: Operation success status: True - Success, False - Failure
        """
        if device is None:
            return False

        if device.name in self.devices.keys():
            return False

        self.devices[device.name] = device

        return True

    def add_enum(self, enum: "Enum") -> bool:
        """Add a Enum to Spec.

        :param enum: Enum to be added
        :return: Operation success status: True - Success, False - Failure
        """

        if enum == None:
            return False

        if enum.name in self.enums.keys():
            return False

        self.enums[enum.name] = enum

        return True

    def add_log(self, log: "Log") -> bool:
        """Add a Log to Spec.

        :param log: Log to be added
        :return: Operation success status: True - Success, False - Failure
        """

        if log == None:
            return False

        if log.name in self.logs.keys():
            return False

        self.logs[log.name] = log

        return True

    def get_common(self) -> Optional["Common"]:
        return self.common

    def get_device(self, name: Union[str, int]) -> Optional["Device"]:
        """Get a Device from Spec by its name.

        :param name: Device name.
        :return: Device or None if not found.
        """

        if type(name) == str:
            return self.devices.get(name)
        if type(name) == int:
            for device in self.devices.values():
                if device.id == name:
                    return device

    def get_log(self, name: str) -> Optional["Log"]:
        """Get a Log from Spec by its name.

        :param name: Log name.
        :return: Log or None if not found.
        """
        return self.logs.get(name)

    def get_signals(self) -> List[Signal]:
        for dev in self.devices.values():
            for msg in dev.msgs.values():
                for signal in msg.signals.values():
                    yield signal

    def rm_node(self, node: Any) -> None:
        """Remove a node from Spec.

        :param node: node to be removed.
        """
        if type(node) == Device:
            self.rm_device(node)
        elif type(node) == Message:
            self.rm_message(node)
        elif type(node) == Signal:
            self.rm_signal(node)
        elif type(node) == Config:
            self.rm_config(node)
        elif type(node) == Command:
            self.rm_cmd(node)
        elif type(node) == Log:
            self.rm_log(node)
        elif type(node) == Enum:
            self.rm_enum(node)
        elif type(node) == EnumValue:
            self.rm_enum_value(node)

    def rm_device(self, device: "Device") -> None:
        """Remove a Device from Spec.

        :param device: Device to be removed.
        """
        devs = [dev.name for dev in self.devices.values() if dev == device]

        for name in devs:
            del self.devices[name]

    def rm_message(self, message: "Message") -> None:
        """Remove a Message from Spec.

        :param message: Message to be removed.
        """
        for dev in self.devices.values():
            msgs = []
            for msg in dev.msgs.values():
                if msg == message:
                    msgs.append(msg.name)

            for name in msgs:
                dev.rm_msg(name)

    def rm_signal(self, signal: "Signal") -> None:
        """Remove a Signal from Spec.

        :param signal: Signal to be removed.
        """

        for dev in self.devices.values():
            for msg in dev.msgs.values():
                signals = []
                for sig in msg.signals.values():
                    if sig is signal:
                        signals.append(signal.name)

                for name in signals:
                    msg.rm_signal(name)

    def rm_config(self, config: "Config") -> None:
        """Remove a Config from Spec.

        :param config: Config to be removed.
        """

        for dev in self.devices.values():
            cfgs = []
            for cfg in dev.cfgs.values():
                if cfg is config:
                    cfgs.append(cfg.name)

            for name in cfgs:
                dev.rm_cfg(name)

    def rm_cmd(self, command: "Command") -> None:
        """Remove a Command from Spec.

        :param command: Command to be removed.
        """

        for dev in self.devices.values():
            cmds = []
            for cmd in dev.cfgs.values():
                if cmd is command:
                    cmds.append(cmd)

            for name in cmds:
                dev.rm_cmd(name)

    def rm_log(self, log):
        """Remove a Log from Spec.

        :param log: Log to be removed.
        """
        logs = []

        for l in self.logs.values():
            if log is l:
                logs.append(l.name)

        for name in logs:
            del self.logs[name]

    def rm_enum(self, enum):
        """Remove a Enum from Spec.

        :param log: Enum to be removed.
        """
        enums = []

        for l in self.enums.values():
            if enum is l:
                enums.append(l.name)

        for name in enums:
            del self.enums[name]

    def rm_enum_value(self, enum_value):
        """Remove a Enum from Spec.

        :param log: EnumValue to be removed.
        """

        for e in self.enums.values():
            enum_values = []
            for ev in e.enumeration.values():
                if enum_value is ev:
                    enum_values.append(ev.name)

            for name in enum_values:
                del e.enumeration[name]

    def compile(self) -> Dict[str, Any]:
        """Transform python class node to its dictionary representation.

        :return: A dictionary containing the node parameters
        """


        d = {"devices": {}, "logs": {}, "enums": {}}

        for dev_k, dev_v in self.devices.items():
            d["devices"][dev_k] = dev_v.compile()


        for log in self.logs.values():
            d["logs"][log.name] = log.compile()



        for enum_k, enum_v in self.enums.items():
            d["enums"][enum_k] = enum_v.compile()


        d["common"] = self.common.compile()
        d["version"] = self.version


        return d

    def decompile(self, d: Dict[str, Any]) -> None:
        """Transform node dictionary representation into a python class.

        :param d: Node dictionary
        """
        d = copy.copy(d)
        self.devices = {}
        self.logs = {}
        self.common.decompile(d["common"])

        for k, v in handle_key_not_found(d, "devices"):
            dev = Device(self)
            dev.decompile(v)
            self.devices[k] = dev

        for k, v in handle_key_not_found(d, "logs"):
            log = Log(self)
            log.decompile(v)
            self.logs[k] = log

        for k, v in handle_key_not_found(d, "enums"):
            enum = Enum(self)
            enum.decompile(v)
            self.enums[k] = enum

        self.version = d["version"]

    def normalize(self):
        """ Update devices and logs dictionary keys.  """

        normalize(self.devices)
        normalize(self.logs)

        normalize(self.enums)
        for enum in self.enums.values():
            enum.normalize()

        for key, dev in self.devices.items():
            dev.normalize()

    def __repr__(self):

        msg_count = 0
        cfg_count = 0
        cmd_count = 0
        sig_count = 0

        for dev in self.devices.values():
            for msg in dev.msgs.values():
                msg_count += 1
                for sig in msg.signals.values():
                    sig_count += 1
            for cfg in dev.cfgs.values():
                cfg_count += 1
            for cmd in dev.cmds.values():
                cmd_count += 1

        return f"(Spec: devs={len(self.devices)}, msgs={msg_count}, sigs={sig_count}, logs={len(self.logs)}, cfgs={cfg_count}, cmds={cmd_count})"


def decompose_id(sid: int) -> Tuple[int, int]:
    """ Find the dev_id and the msg_id from the sid."""
    return sid & 0x1F, (sid >> 5) & 0x3F


def make_sid(dev_id: int, msg_id: int) -> int:
    """ Find the sid from the dev_id and the msg_id """
    return (msg_id << 5) + dev_id
