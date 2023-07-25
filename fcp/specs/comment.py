from pydantic import BaseModel
from typing import *


class Comment(BaseModel):
    value: str

    def to_dict(self):
        return self.value
