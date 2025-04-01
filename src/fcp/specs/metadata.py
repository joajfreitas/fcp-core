# Copyright (c) 2024 the fcp AUTHORS.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Metadata."""

from serde import serde, strict
from beartype.typing import Dict, Any


@serde(type_check=strict)
class MetaData:
    """MetaData information for AST nodes."""

    line: int
    end_line: int
    column: int
    end_column: int
    start_pos: int
    end_pos: int
    filename: str

    def __init__(
        self,
        line: int,
        end_line: int,
        column: int,
        end_column: int,
        start_pos: int,
        end_pos: int,
        filename: str,
    ):
        self.line = line
        self.end_line = end_line
        self.column = column
        self.end_column = end_column
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.filename = filename

    def reflection(self) -> Dict[str, Any]:
        """Reflection."""
        return {
            "line": self.line,
            "end_line": self.end_line,
            "column": self.column,
            "end_column": self.end_column,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "filename": self.filename,
        }
