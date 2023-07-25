import sys
from typing import *
from pydantic import BaseModel
import datetime
import logging

from .metadata import MetaData
from .comment import Comment
from .type import Type


class SignalValueError(Exception):
    pass


class Signal(BaseModel):
    name: str
    field_id: int
    type: Type
    scale: Optional[float] = 1.0
    offset: Optional[float] = 0.0
    unit: Optional[str]
    description: Optional[Comment]
    min_value: Optional[float]
    max_value: Optional[float]
    byte_order: Optional[str] = "little_endian"
    meta: Optional[MetaData]

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
            "description": self.comment.to_dict(),
        }

    def __repr__(self):
        return f"<Signal {self.name} {self.type}>"
