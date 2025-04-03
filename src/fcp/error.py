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

"""Error."""

from beartype.typing import Any, Tuple
from typing_extensions import Self
from enum import Enum
from inspect import getframeinfo, stack
from pathlib import Path


class Level(Enum):
    """Log level."""

    Debug = 0
    Info = 1
    Warn = 2
    Error = 3


class FcpError:
    """Fcp error."""

    def __init__(self, msg: str, node: Any = None):
        caller = getframeinfo(stack()[1][0])
        self.msg = [(msg, node, (Path(caller.filename), caller.lineno))]

    def results_in(self, msg: str, node: Any = None) -> Self:
        """Appends error message to the current error."""
        caller = getframeinfo(stack()[1][0])
        self.msg.append((msg, node, (Path(caller.filename), caller.lineno)))
        return self
