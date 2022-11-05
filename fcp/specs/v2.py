from typing import Tuple
import copy
import datetime
import time
import logging
from serde import Model, fields

from . import v1
from . import device
from . import log
from . import broadcast
from . import config
from . import cmd
from . import signal
from . import enum
from . import struct


def handle_key_not_found(d: dict, key: str):
    return d.get(key).items() if d.get(key) != None else []


class FcpV2(Model):
    """FCP root node. Holds all Devices, Messages, Signals, Logs, Configs,
    Commands and Arguments.
    """

    structs: fields.List(struct.Struct)
    enums: fields.List(enum.Enum)
    devices: fields.List(device.Device)
    broadcasts: fields.List(broadcast.Broadcast)
    logs: fields.List(log.Log)
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
        nodes = [node.to_fcp() for node in self.enums + self.structs]
        fcp_structure = {}

        for node in nodes:
            if node[0] not in fcp_structure.keys():
                fcp_structure[node[0]] = []
            fcp_structure[node[0]].append(node[1])

        return fcp_structure

    def to_fpi(self):
        nodes = [node.to_fpi() for node in self.devices + self.broadcasts + self.logs]
        fpi_structure = {}

        for node in nodes:
            if node[0] not in fpi_structure.keys():
                fpi_structure[node[0]] = []
            fpi_structure[node[0]].append(node[1])

        return fpi_structure

    def __repr__(self) -> str:
        sig_count = len([sig for struct in self.structs for sig in struct.signals])
        return f"(Spec: devs={len(self.devices)}, broadcasts={len(self.broadcasts)}, structs={len(self.structs)}, sigs={sig_count})"


def decompose_id(sid: int) -> Tuple[int, int]:
    """Find the dev_id and the msg_id from the sid."""
    return sid & 0x1F, (sid >> 5) & 0x3F


def make_sid(dev_id: int, msg_id: int) -> int:
    """Find the sid from the dev_id and the msg_id"""
    return (msg_id << 5) + dev_id
