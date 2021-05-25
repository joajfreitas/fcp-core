from typing import *
import datetime

from ..can import CANMessage

from .node import Node

class SignalValueError(Exception):
    pass

class Signal(Node):
    """
    Signal node. Represents a CAN signal, similar to a DBC signal.

    :param name: Name of the Signal.
    :param start: Start bit
    :param length: Signal bit size.
    :param scale: Scaling applied to the signal's data.
    :param offset: Offset applied to the signal's data.
    :param unit: Unit of the Signal after applying scaling and offset.
    :param comment: Description of the Signal.
    :param min_value: Minimum value allowed to the Signal's data.
    :param max_value: Maximum value allowed to the Signal's data.
    :param type: Type of the Signal's data.
    :param mux: Name of the mux Signal. None if the Signal doesn't belong to a multiplexed Message.
    :param mux_count: Number of signals that the mux can reference for this Muxed signal.


    """

    def __init__(
        self,
        parent: "Message" = None,
        name: str = "",
        start: int = 0,
        length: int = 0,
        scale: float = 1.0,
        offset: float = 0.0,
        unit: str = "",
        comment: str = "",
        min_value: float = 0.0,
        max_value: float = 0.0,
        type: str = "unsigned",
        byte_order: str = "little_endian",
        mux: str = "",
        mux_count: int = 1,
        alias: str = "",
    ):

        assert parent is not None
        self.parent = parent
        m = max(
            [
                int(sig.name[3:])
                for sig in self.parent.signals.values()
                if sig.name.startswith("sig")
            ]
            + [0]
        )
        self._name = name or ("sig" + str(m + 1))
        self._start = start
        self._length = length
        self._scale = scale
        self._offset = offset
        self._unit = unit
        self._comment = comment
        self._min_value = min_value
        self._max_value = max_value
        self._type = type
        self._byte_order = byte_order
        self._mux = mux
        self._mux_count = mux_count
        self._alias = alias

        self.creation_date = datetime.datetime.now()

    @property
    def name(self) -> str:
        return self._name

    @property
    def start(self) -> int:
        return self._start

    @property
    def length(self) -> int:
        return self._length

    @property
    def scale(self) -> float:
        return self._scale

    @property
    def offset(self) -> float:
        return self._offset

    @property
    def unit(self) -> str:
        return self._unit

    @property
    def comment(self) -> str:
        return self._comment

    @property
    def min_value(self) -> float:
        return self._min_value

    @property
    def max_value(self) -> float:
        return self._max_value

    @property
    def type(self) -> str:
        return self._type

    @property
    def byte_order(self) -> str:
        return self._byte_order

    @property
    def mux(self) -> str:
        return self._mux

    @property
    def mux_count(self) -> int:
        return self._mux_count

    @property
    def alias(self) -> str:
        return self._alias

    @name.setter
    def name(self, name: str) -> None:
        try:
            self._name = name
        except Exception as e:
            return
    @start.setter
    def start(self, start: int) -> None:
        try:
            self._start = int(start)
        except Exception as e:
            return

    @length.setter
    def length(self, length: int) -> None:
        try:
            self._length = int(length)
        except Exception as e:
            return

    @scale.setter
    def scale(self, scale: float) -> None:
        try:
            self._scale = float(scale)
        except Exception as e:
            return

    @offset.setter
    def offset(self, offset: float) -> None:
        try:
            self._offset = float(offset)
        except Exception as e:
            return

    @unit.setter
    def unit(self, unit: str) -> None:
        try:
            self._unit = unit
        except Exception as e:
            return

    @comment.setter
    def comment(self, comment: str) -> None:
        try:
            self._comment = comment
        except Exception as e:
            return

    @min_value.setter
    def min_value(self, min_value: float) -> None:
        try:
            self._min_value = float(min_value)
        except Exception as e:
            return

    @max_value.setter
    def max_value(self, max_value: float) -> None:
        try:
            self._max_value = float(max_value)
        except Exception as e:
            return

    @type.setter
    def type(self, type: str) -> None:
        try:
            self._type = type
        except Exception as e:
            return

    @byte_order.setter
    def byte_order(self, byte_order: str) -> None:
        try:
            self._byte_order = byte_order
        except Exception as e:
            return

    @mux.setter
    def mux(self, mux: str) -> None:
        try:
            self._mux = mux
        except Exception as e:
            return

    @mux_count.setter
    def mux_count(self, mux_count: int) -> None:
        try:
            self._mux_count = int(mux_count)
        except Exception as e:
            return

    @alias.setter
    def alias(self, alias: str) -> None:
        try:
            self._alias = alias
        except Exception as e:
            return

    def compile(self) -> Dict[str, Any]:
        """Transform python class node to its dictionary representation.

        :return: A dictionary containing the node parameters
        """

        return self.make_public(self, self.filter_private(self.__dict__))

    def decompile(self, d: Dict[str, Any]) -> None:
        """Transform node dictionary representation into a python class.

        :param d: Node dictionary
        """
        for k,v in self.make_private(self, d).items():
            self.__setattr__(k,v)

    def bitmask(self, n):
        return 2 ** n - 1

    def encode(self, value) -> int:
        if value>2**self.length:
            raise SignalValueError()
        value = (value-self.offset) / self.scale
        return (int(value) & self.bitmask(self.length)) << self.start

    def decode(self, msg: CANMessage):
        data64 = msg.get_data64()
        value = (data64 >> self.start) & self.bitmask(self.length)
        if self.type == "signed" and value >> (self.length - 1) == 1:
            value = -((value ^ self.bitmask(self.length)) + 1);
        return self.scale * value - self.offset

    def __hash__(self):
        return hash((self.name, self.start, self.length, self.creation_date))

    def __repr__(self):
        return f"<Signal name={self.name} start={self.start} end={self.length} scale={self.scale} offset={self.offset}>"
