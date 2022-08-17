from typing import *
import datetime
from serde import Model, fields

from ..can import CANMessage
from .node import Node, Transmit
from .signal import Signal
from ..can import CANMessage
from .utils import normalize


class Message(Model):
    """Message node, Represents a CAN message, similar to a DBC message.

    :param name: Name of the Message.
    :param id: FST Message identifier, highest 6 bits of the identifier.
    :param dlc: Message DLC.
    :param signals: Dictionary containing the Message signals.
    :param frequency: Transmission period in millisecond. If 0 message
    isn't automatically sent.
    """

    id: fields.Int()
    name: fields.Str()
    dlc: fields.Int()
    signals: fields.List(Signal)
    description: fields.Str()
    device: fields.Str()

    def to_fcp(self):
        return (
            f"struct {self.name} {{\n"
            + "\n".join([signal.to_fcp() for signal in self.signals])
            + "\n}\n"
        )

    def to_idl(self) -> str:
        def show(value, default, fmt):
            if value == default:
                return ""
            else:
                return fmt.format((value))

        output = show(self.description, "", "/*{}*/\n")
        output += f'message {self.name}: device("{self.device}") | id({self.id}) | dlc({self.dlc}) {{ \n'
        for signal in self.signals:
            output += signal.to_idl() + "\n"

        output += "}\n"

        return output

    def encode(self, signals, src=None):
        assert not ((src is None) and (type(self.parent) == "Common"))
        dev_id = src if src is not None else self.parent.id
        data = 0
        for name, sig in signals.items():
            assert self.signals.get(name) is not None
            data |= self.signals.get(name).encode(sig)

        data16 = [
            (data >> 0) & 0xFFFF,
            (data >> 16) & 0xFFFF,
            (data >> 32) & 0xFFFF,
            (data >> 48) & 0xFFFF,
        ]

        sid = (self.id << 5) + self.parent.id
        msg = CANMessage(sid=sid, dlc=self.dlc, data16=data16, timestamp=0)

        return msg

    def decode(self, msg: CANMessage):
        mux = ""
        signals = {}
        for name, signal in self.signals.items():
            is_muxed = 0
            if signal.mux_count != 1:
                is_muxed = 1
                mux = signal.mux
            signals[name] = (signal.decode(msg), is_muxed)

        if mux != "":
            mux_value = str(int(signals[mux][0]))
        else:
            mux_value = None

        signals = {k + (mux_value if v[1] else ""): v[0] for (k, v) in signals.items()}

        return self.name, signals

    def __hash__(self):
        return hash((self.name, self.id, self.creation_date))

    def __repr__(self):
        return f"<Message name={self.name} id={self.id}>"
