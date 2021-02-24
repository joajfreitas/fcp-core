from typing import *
import datetime

from ..can import CANMessage
from .node import Node, Transmit
from .signal import Signal
from ..can import CANMessage
from .utils import normalize

class Message(Transmit):
    """Message node, Represents a CAN message, similar to a DBC message.

    :param name: Name of the Message.
    :param id: FST Message identifier, highest 6 bits of the identifier.
    :param dlc: Message DLC.
    :param signals: Dictionary containing the Message signals.
    :param frequency: Transmission period in millisecond. If 0 message
    isn't automatically sent.
    """

    def __init__(
        self,
        parent: "Device" = None,
        name: str = "",
        id: int = 0,
        dlc: int = 8,
        signals: Dict[str, Signal] = None,
        frequency: int = 0,
        description: str = "",
    ):

        assert parent is not None
        self.parent = parent

        self._id = id or max([msg.id for msg in self.parent.msgs.values()] + [0]) + 1
        self._name = name or ("msg" + str(self.id))
        self._dlc = dlc
        self.signals = {} if signals == None else signals
        self._frequency = frequency
        self._description = description

        self.creation_date = datetime.datetime.now()

    @property
    def name(self) -> str:
        return self._name

    @property
    def id(self) -> int:
        return self._id

    @property
    def dlc(self) -> int:
        return self._dlc

    @property
    def frequency(self) -> int:
        return self._frequency

    @property
    def description(self) -> str:
        return self._description

    @name.setter
    def name(self, name: str) -> None:
        try:
            self._name = name
        except Exception as e:
            return

    @id.setter
    def id(self, id: int) -> None:
        try:
            self._id = int(id)
        except Exception as e:
            return

    @dlc.setter
    def dlc(self, dlc: int) -> None:
        try:
            self._dlc = int(dlc)
        except Exception as e:
            return

    @frequency.setter
    def frequency(self, frequency: int) -> None:
        try:
            self._frequency = int(frequency)
        except Exception as e:
            return

    @description.setter
    def description(self, description: str) -> None:
        try:
            self._description = description
        except Exception as e:
            return


    def compile(self) -> Dict[str, Any]:
        """Transform python class node to its dictionary representation.

        :return: A dictionary containing the node parameters
        """

        sigs = {}
        for k, v in self.signals.items():
            sigs[k] = v.compile()

        d = self.make_public(self, self.filter_private(self.__dict__))
        d["signals"] = sigs
        return d

    def decompile(self, d: Dict[str, Any]) -> None:
        """Transform node dictionary representation into a python class.

        :param d: Node dictionary
        """
        signals = d["signals"]
        for k,v in self.make_private(self,d).items():
            self.__setattr__(k,v)

        for key, value in signals.items():
            sig = Signal(self)
            sig.decompile(value)
            self.signals[key] = sig

    def add_signal(self, signal: Signal) -> bool:
        """Add a Signal to Message.

        :param signal: Signal to be added
        :return: Operation success status: True - Success, False - Failure
        """

        if signal == None:
            return False

        if signal.name in self.signals.keys():
            self.signals[signal.name].mux_count += 1
            return True

        self.signals[signal.name] = signal

        return True

    def get_signal(self, name: str) -> Optional[Signal]:
        """Get a Signal from Message by its name.

        :param name: Signal name.
        :return: Signal or None if not found.
        """
        return self.signals.get(name)


    def rm_signal(self, name: str) -> bool:
        """Remove a Signal from Spec.

        :param signal: Signal to be removed.
        """
        if self.get_signal(name) is None:
            return False

        del self.signals[name]
        return True

    def normalize(self):
        """ Update signals dictionary keys."""
        normalize(self.signals)

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
            (data >> 48) & 0xFFFF]

        sid = (self.id << 5) + self.parent.id
        msg = CANMessage(sid=sid, dlc=self.dlc, data16 = data16, timestamp = 0)

        return msg

    def decode(self, msg: CANMessage):
        mux = ""
        signals = {}
        for name, signal in self.signals.items():
            if signal.mux_count != 1:
                mux = signal.mux
            signals[name] = signal.decode(msg)

        if mux != "":
            mux_value = str(int(signals[mux]))
            signals = {k + (mux_value if k != mux else ""):v for (k,v) in signals.items()}

        return self.name, signals

    def __hash__(self):
        return hash((self.name, self.id, self.creation_date))

    def __repr__(self):
        return f"<Message name={self.name} id={self.id}>"
