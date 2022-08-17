from typing import *
import copy
import datetime
import time
from serde import Model, fields

from . import *
from .utils import normalize


def handle_key_not_found(d: dict, key: str):
    return d.get(key).items() if d.get(key) != None else []


class Spec(Model):
    """FCP root node. Holds all Devices, Messages, Signals, Logs, Configs,
    Commands and Arguments.
    """

    devices: fields.List(Device)
    messages: fields.List(Message)
    commands: fields.List(Command)
    configs: fields.List(Config)
    logs: fields.List(Log)
    enums: fields.List(Enum)
    version: fields.Str()

    def to_fcp(self):
        return "\n".join([msg.to_fcp() for msg in self.messages])

    def to_idl(self):
        output = ""

        for device in self.devices:
            output += device.to_idl()

        output += "\n"

        for device in self.devices:
            for msg in self.get_messages(device.name):
                output += msg.to_idl() + "\n"

            for config in self.get_configs(device.name):
                output += config.to_idl() + "\n"

            output += "\n"

            for command in self.get_commands(device.name):
                output += command.to_idl() + "\n"

        for log in self.logs:
            output += log.to_idl() + "\n"

        return output

    def get_messages(self, id=None):
        if id is None:
            return [message for message in self.messages]
        else:
            return [message for message in self.messages if message.device == id]

    def get_configs(self, id=None):
        if id is None:
            return [config for config in self.configs]
        else:
            return [config for config in self.configs if config.device == id]

    def get_commands(self, id=None):
        if id is None:
            return [command for command in self.commands]
        else:
            return [command for command in self.commands if command.device == id]

    def __repr__(self) -> str:

        msg_count = 0
        cfg_count = 0
        cmd_count = 0
        sig_count = 0

        for dev in self.devices:
            for msg in self.get_messages(id=dev.name):
                msg_count += 1
                for sig in msg.signals:
                    sig_count += 1
            for cfg in self.get_configs(id=dev.name):
                cfg_count += 1
            for cmd in self.get_commands(id=dev.name):
                cmd_count += 1

        return f"(Spec: devs={len(self.devices)}, msgs={msg_count}, sigs={sig_count}, logs={len(self.logs)}, cfgs={cfg_count}, cmds={cmd_count})"


def decompose_id(sid: int) -> Tuple[int, int]:
    """Find the dev_id and the msg_id from the sid."""
    return sid & 0x1F, (sid >> 5) & 0x3F


def make_sid(dev_id: int, msg_id: int) -> int:
    """Find the sid from the dev_id and the msg_id"""
    return (msg_id << 5) + dev_id
