from typing import *
import copy
import datetime
import time
import logging
from serde import Model, fields

from . import (
    Device,
    Config,
    Command,
    Signal,
    Enum,
    EnumValue,
    Log,
    Struct,
    Broadcast,
)
from .utils import normalize


def handle_key_not_found(d: dict, key: str):
    return d.get(key).items() if d.get(key) != None else []


class FcpV2(Model):
    """FCP root node. Holds all Devices, Messages, Signals, Logs, Configs,
    Commands and Arguments.
    """

    devices: fields.List(Device)
    structs: fields.List(Struct)
    broadcasts: fields.List(Broadcast)
    enums: fields.List(Enum)
    version: fields.Str(default="1.0")

    def add_device(self, device):
        self.devices.append(device)

    def get_broadcasts(self, device=None):
        if device is None:
            return [broadcast for broadcast in self.broadcasts]
        else:
            return [
                broadcast
                for broadcast in self.broadcasts
                if broadcast.field["device"] == device
            ]

    def to_fcp(self):
        return "\n\n".join([node.to_fcp() for node in self.enums + self.structs])

    def to_fpi(self):
        return "\n".join([node.to_fpi() for node in self.devices + self.broadcasts])

    def __repr__(self) -> str:

        sig_count = len([sig for struct in self.structs for sig in struct.signals])

        return f"(Spec: devs={len(self.devices)}, broadcasts={len(self.broadcasts)}, structs={len(self.structs)}, sigs={sig_count})"


def decompose_id(sid: int) -> Tuple[int, int]:
    """Find the dev_id and the msg_id from the sid."""
    return sid & 0x1F, (sid >> 5) & 0x3F


def make_sid(dev_id: int, msg_id: int) -> int:
    """Find the sid from the dev_id and the msg_id"""
    return (msg_id << 5) + dev_id
