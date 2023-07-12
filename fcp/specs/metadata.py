from pydantic import BaseModel
from typing import *


class MetaData(BaseModel):
    line: int
    end_line: int
    column: int
    end_column: int
    start_pos: int
    end_pos: int
    filename: str
