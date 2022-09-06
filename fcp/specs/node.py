from typing import *

from ..can import CANMessage


class Node:
    def filter_private(self, d: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for (k, v) in d.items() if k.startswith("_")}

    def make_private(self, obj, d: Dict[str, Any]) -> Dict[str, Any]:
        new_d = {}
        for key in d.keys():
            T = type(getattr(obj, key))
            new_d["_" + key] = T(d[key])
        return new_d

    def make_public(self, obj, d: Dict[str, Any]) -> Dict[str, Any]:
        return {k[1:] if k.startswith("_") else k: v for (k, v) in d.items()}


class Transmit(Node):
    def encode(self):
        print("encode not implemented")
        assert False

    def decode(self, msg: CANMessage):
        print("decode not implemented")
        assert False

    pass
