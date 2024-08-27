from typing import Any, Optional
from serde import serde, strict
from typing import Optional

from .metadata import MetaData
from .comment import Comment


class SignalValueError(Exception):
    pass


@serde(type_check=strict)
class Signal:
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

    name: str
    start: Optional[int]
    unit: Optional[str]
    comment: Optional[Comment]
    length: Optional[int]
    min_value: Optional[float]
    max_value: Optional[float]
    field_id: int
    meta: Optional[MetaData]
    scale: Optional[float] = 1.0
    offset: Optional[float] = 0.0
    type: Optional[str] = "unsigned"
    byte_order: Optional[str] = "little_endian"
    mux: Optional[str] = ""
    mux_count: Optional[int] = 1

    def to_fcp(self) -> str:
        def show(value: Any, default: Any, fmt: Any):
            if value == default:
                return ""
            else:
                return fmt.format((value))

        def show2(value1: Any, default1: Any, value2: Any, default2: Any, fmt: Any):
            if value1 == default1 and value2 == default2:
                return ""
            else:
                return fmt.format(value1, value2)

        return (
            (f"\t/*{self.comment.value}*/\n" if self.comment.value != "" else "")
            + f"\t{self.name} @{self.field_id}: {self.type} "
            + show2(self.scale, 1.0, self.offset, 0.0, "| scale({}, {})")
            + show2(self.min_value, 0.0, self.max_value, 0.0, "| range({}, {})")
            + show2(self.mux, "", self.mux_count, 1, '| mux("{}", {})')
            + show(self.byte_order, "little", '| endianess("{}")')
            + show(self.unit, "", '| unit("{}")')
        )

    def __repr__(self) -> str:
        return f"<Signal name={self.name} start={self.start} end={self.length} scale={self.scale} offset={self.offset}>"
