import copy
import datetime
import time
import logging
from pydantic import BaseModel
from typing import *

from . import signal
from . import enum
from . import struct


def handle_key_not_found(d: dict, key: str):
    return d.get(key).items() if d.get(key) != None else []


class FcpV2(BaseModel):
    """FCP root node. Holds all Devices, Messages, Signals, Logs, Configs,
    Commands and Arguments.
    """

    structs: List[struct.Struct]
    enums: List[enum.Enum]
    version: str = "3.0"

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

    def get_type(self, name):
        for enum in self.enums:
            if enum.name == name:
                return enum

        for struct in self.structs:
            if struct.name == name:
                return struct

        return None

    def get_broadcast(self, name):
        for broadcast in self.broadcasts:
            if broadcast.name == name:
                return broadcast

        return None

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

    def to_dict(self):
        return {
            "structs": [struct.to_dict() for struct in self.structs],
            "enums": [enum.to_dict() for enum in self.enums],
            "devices": [device.to_dict() for device in self.devices],
            "broadcasts": [broadcast.to_dict() for broadcast in self.broadcasts],
        }

    def get_builtin_types(self):
        builtin_types = ["u" + str(i) for i in range(1, 65)]
        builtin_types += ["i" + str(i) for i in range(1, 65)]
        builtin_types += ["f32", "f64"]

        return builtin_types

    def get_size(self, type):
        builtin_types = self.get_builtin_types()

        if type in builtin_types:
            return int(type[1:])
        elif isinstance(type, enum.Enum):
            return type.get_size()
        elif isinstance(type, struct.Struct):
            return 0
        else:
            raise IndexError

    def __repr__(self) -> str:
        sig_count = len([sig for struct in self.structs for sig in struct.signals])
        return f"(Spec: devs={len(self.devices)}, broadcasts={len(self.broadcasts)}, structs={len(self.structs)}, sigs={sig_count})"
