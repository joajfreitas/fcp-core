from pydantic import BaseModel
from typing import *

from .metadata import MetaData

from .type import Type


class Signal(BaseModel):
    name: str
    field_id: int
    type: str
    size: int
    repeat: int
    meta: MetaData


class Struct(BaseModel):
    name: str
    signals: List[Signal]
    meta: MetaData


def convert_struct(structs, enums, struct):
    for signal in struct.signals:
        pass


def l2(fcp):
    structs = {struct.name: struct for struct in fcp.structs}
    enums = {enum.name: enum for enum in fcp.enums}
    for struct in fcp.structs:
        struct = convert_struct(structs, enums, struct)
