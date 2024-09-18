from typing import Tuple, Any, Optional, Callable, Dict
from serde import serde, strict, to_dict
import struct

from . import device
from . import log
from . import broadcast
from . import enum
from .signal import Signal
from .struct import Struct


def handle_key_not_found(d: dict[str, Any], key: str) -> list[Any]:
    return d.get(key).items() if d.get(key) is not None else []  # type: ignore


@serde(type_check=strict)
class FcpV2:
    """FCP root node. Holds all Devices, Messages, Signals, Logs, Configs,
    Commands and Arguments.
    """

    structs: list[Struct]
    enums: list[enum.Enum]
    devices: list[device.Device]
    broadcasts: list[broadcast.Broadcast]
    logs: list[log.Log]
    version: str = "1.0"

    def add_device(self, device: device.Device) -> None:
        self.devices.append(device)

    def get_broadcasts(
        self, device: Optional[device.Device] = None
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

    def to_dict(self) -> Any:
        def filter_tree(filter: Callable[[Any, Any], bool]) -> Callable[[Any], Any]:
            def closure(tree: Any) -> Any:
                if isinstance(tree, dict):
                    return {k: closure(v) for k, v in tree.items() if filter(k, v)}
                elif isinstance(tree, list):
                    return [closure(x) for x in tree]
                else:
                    return tree

            return closure

        remove_none_fields = filter_tree(lambda k, v: v is not None)
        remove_meta = filter_tree(lambda k, v: k != "meta")

        return remove_meta(remove_none_fields(to_dict(self)))

    def __repr__(self) -> str:
        sig_count = len([sig for struct in self.structs for sig in struct.signals])
        return f"(Spec: devs={len(self.devices)}, broadcasts={len(self.broadcasts)}, structs={len(self.structs)}, sigs={sig_count})"


def decompose_id(sid: int) -> Tuple[int, int]:
    """Find the dev_id and the msg_id from the sid."""
    return sid & 0x1F, (sid >> 5) & 0x3F


def make_sid(dev_id: int, msg_id: int) -> int:
    """Find the sid from the dev_id and the msg_id"""
    return (msg_id << 5) + dev_id


def default_serialization(fcp: FcpV2, typename: str, data: Dict[str, Any]) -> bytearray:
    """
    ```fcp
    struct foo {
        var1: u8;
        var2: u16;
    };

    struct bar {
        var1: foo;
        var2: f32;
    };
    ```

    data:

    {
        "var1":
            {
                "var1": 4,
                "var2": 257
            },
        "var2": 10.1
    }

    [4, 1, 1, 65, 33, 153, 154]
    """

    structs = {struct.name: struct for struct in fcp.structs}

    def serialize_signal(signal: Signal, value: Dict["str", Any] | Any) -> bytearray:
        conversions: Dict[str, Callable[[Any], bytearray]] = {
            "u8": lambda x: x.to_bytes(1, signed=False, byteorder="little"),
            "u16": lambda x: x.to_bytes(2, signed=False, byteorder="little"),
            "u32": lambda x: x.to_bytes(4, signed=False, byteorder="little"),
            "u64": lambda x: x.to_bytes(8, signed=False, byteorder="little"),
            "i8": lambda x: x.to_bytes(1, signed=True, byteorder="little"),
            "i16": lambda x: x.to_bytes(2, signed=True, byteorder="little"),
            "i32": lambda x: x.to_bytes(4, signed=True, byteorder="little"),
            "i64": lambda x: x.to_bytes(8, signed=True, byteorder="little"),
            "f32": lambda x: bytearray(struct.pack("f", x)),
            "f64": lambda x: bytearray(struct.pack("d", x)),
        }

        if signal.type in conversions.keys():
            return conversions[signal.type](value)
        elif signal.type is not None:
            return serialize_struct(structs[signal.type], value)
        else:
            raise ValueError()

    def serialize_struct(struct: Struct, data: Dict["str", Any]) -> bytearray:
        buffer = bytearray()
        for signal in struct.signals:
            buffer += serialize_signal(signal, data[signal.name])

        return buffer

    return serialize_struct(structs[typename], data)
