from pydantic import BaseModel
from typing import *


class Type(BaseModel):
    base: str
    arity: Optional[int]

    def to_dict(self):
        return {"base": self.base, "arity": self.arity}
