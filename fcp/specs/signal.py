import sys
from typing import *
import datetime
import logging
from serde import Model, fields

from ..can import CANMessage
from .node import Node
from .metadata import MetaData
from .comment import Comment


class SignalValueError(Exception):
    pass


class Signal(Model):
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

    name: fields.Str()
    start: fields.Optional(fields.Int())
    length: fields.Optional(fields.Int())
    scale: fields.Optional(fields.Float(default=1.0))
    offset: fields.Optional(fields.Float(default=0.0))
    unit: fields.Optional(fields.Str())
    comment: fields.Optional(Comment)
    min_value: fields.Optional(fields.Float())
    max_value: fields.Optional(fields.Float())
    type: fields.Optional(fields.Str(default="unsigned"))
    byte_order: fields.Optional(fields.Str(default="little_endian"))
    mux: fields.Optional(fields.Str(default=""))
    mux_count: fields.Optional(fields.Int(default=1))
    meta: fields.Optional(MetaData)

    def to_fcp(self):
        unit = (
            f' | unit("{self.unit}")'
            if self.unit is not None and self.unit != ""
            else ""
        )
        return (
            (f"\t/*{self.comment.value}*/\n" if self.comment.value != "" else "")
            + f"\t{self.name}: {self.type}"
            + unit
        )

    def __repr__(self):
        return f"<Signal name={self.name} start={self.start} end={self.length} scale={self.scale} offset={self.offset}>"
