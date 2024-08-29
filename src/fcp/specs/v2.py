from typing import Tuple, Any
from serde import serde, strict

from . import device
from . import log
from . import broadcast
from . import enum
from . import struct


def handle_key_not_found(d: dict[str, Any], key: str) -> list[Any]:
    return d.get(key).items() if d.get(key) is not None else []  # type: ignore


@serde(type_check=strict)
class FcpV2:
    """FCP root node. Holds all Devices, Messages, Signals, Logs, Configs,
    Commands and Arguments.
    """

<<<<<<< HEAD
    structs: fields.List(struct.Struct)
    enums: fields.List(enum.Enum)
    devices: fields.List(device.Device)
    broadcasts: fields.List(broadcast.Broadcast)
    logs: fields.List(log.Log)
    version: fields.Str()
=======
    structs: list[struct.Struct]
    enums: list[enum.Enum]
    devices: list[device.Device]
    broadcasts: list[broadcast.Broadcast]
    logs: list[log.Log]
    version: str = "1.0"
<<<<<<< HEAD
>>>>>>> f20376f (Changed old serde to pyserde)
=======
>>>>>>> 925c042 (backup)

    def add_device(self, device: device.Device) -> None:
        self.devices.append(device)

    def get_broadcasts(
        self, device: device.Device | None = None
    ) -> list[broadcast.Broadcast]:
        if device is None:
            return [broadcast for broadcast in self.broadcasts]
        else:
            return [
                broadcast
                for broadcast in self.broadcasts
                if broadcast.field["device"] == device
            ]

    def to_fcp(self) -> dict[str, list[dict[str, Any]]]:
        nodes = [node.to_fcp() for node in self.enums + self.structs]
        fcp_structure: dict[str, list[Any]] = {}

        for node in nodes:
            if node[0] not in fcp_structure.keys():
                fcp_structure[node[0]] = []
            fcp_structure[node[0]].append(node[1])

        return fcp_structure

    def to_fpi(self) -> dict[str, list[dict[str, Any]]]:
        nodes = [node.to_fpi() for node in self.devices + self.broadcasts + self.logs]
        fpi_structure: dict[str, list[Any]] = {}

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
