import sys
from typing import *
import datetime
import logging
from serde import Model, fields

from .metadata import MetaData
from .comment import Comment
from .type import Type


class SignalValueError(Exception):
    pass


class Signal(Model):
    name: fields.Str()
    field_id: fields.Int()
    type: Type
    start: fields.Optional(fields.Int())
    length: fields.Optional(fields.Int())
    scale: fields.Optional(fields.Float(default=1.0))
    offset: fields.Optional(fields.Float(default=0.0))
    unit: fields.Optional(fields.Str())
    comment: fields.Optional(Comment)
    min_value: fields.Optional(fields.Float())
    max_value: fields.Optional(fields.Float())
    byte_order: fields.Optional(fields.Str(default="little_endian"))
    mux: fields.Optional(fields.Str(default=""))
    mux_count: fields.Optional(fields.Int(default=1))
    meta: fields.Optional(MetaData)

    def to_fcp(self):
        def show(value, default, fmt):
            if value == default:
                return ""
            else:
                return fmt.format((value))

        def show2(value1, default1, value2, default2, fmt):
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

    def to_dict(self):
        return {
                "name": self.name,
                "field_id": self.field_id,
                "type": self.type.to_dict(),
                "unit": self.unit,
                "scale": self.scale,
                "offset": self.offset,
                "min_value": self.min_value,
                "max_value": self.max_value,
                }

    def __repr__(self):
        return f"<Signal {self.name} {self.type}>"
