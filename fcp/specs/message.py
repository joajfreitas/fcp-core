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

    def add_signal(self, signal):
        self.signals.append(signal)

    def to_fcp(self):
        return (
            f"struct {self.name} {{\n"
            + "\n".join([signal.to_fcp() for signal in self.signals])
            + "\n}\n"
        )

    def to_fpi(self):
        pass

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

    def __repr__(self):
        return f"<Message name={self.name} id={self.id}>"
