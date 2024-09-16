from typing import Any, Optional, Union
from serde import serde, strict, field

from .metadata import MetaData
from .comment import Comment, comment_serializer, comment_deserializer


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
    field_id: int
    unit: Optional[str] = None
    comment: Optional[Comment] = field(default=None, serializer=comment_serializer, deserializer=comment_deserializer)
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    meta: Optional[MetaData] = field(skip=True, default=None)
    type: Optional[str] = "unsigned"

    def to_fcp(self) -> str:
        def show(value: Any, default: Any, fmt: Any) -> str:
            if value == default:
                return ""
            else:
                return str(fmt.format((value)))

        def show2(
            value1: Any, default1: Any, value2: Any, default2: Any, fmt: Any
        ) -> Union[str, Any]:
            if value1 == default1 and value2 == default2:
                return ""
            else:
                return fmt.format(value1, value2)

        # if comment is None then return empty string
        comment = self.comment.value if self.comment else ""

        return (
            (f"\t/*{comment}*/\n" if comment != "" else "")
            + f"\t{self.name} @{self.field_id}: {self.type} "
            + show2(self.scale, 1.0, self.offset, 0.0, "| scale({}, {})")
            + show2(self.min_value, 0.0, self.max_value, 0.0, "| range({}, {})")
            + show2(self.mux, "", self.mux_count, 1, '| mux("{}", {})')
            + show(self.byte_order, "little", '| endianess("{}")')
            + show(self.unit, "", '| unit("{}")')
        )

    def __repr__(self) -> str:
        return f"<Signal name={self.name} start={self.start} end={self.length} scale={self.scale} offset={self.offset}>"
