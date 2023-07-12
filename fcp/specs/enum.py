from pydantic import BaseModel
from typing import *

import math
import datetime

from .metadata import MetaData
from .comment import Comment


class Enum(BaseModel):
    """Fcp Enum. C lookalike for FCP type definitions with name-value
    associations.
    """

    name: str
    enumeration: Dict[str, Tuple[int, MetaData]]
    meta: Optional[MetaData]
    description: Optional[Comment]

    def get_type(self):
        return "enum"

    def get_name(self):
        return self.name

    def to_fcp(self):
        return (
            "enum",
            (f"/*{self.comment.value}*/\n" if self.comment.value != "" else "")
            + f"enum {self.name} {{\n\t"
            + "\n\t".join([f"{enum.name}: {enum.value};" for enum in self.enumeration])
            + "\n};",
        )

    def __repr__(self):
        return "name: {}".format(self.name)
