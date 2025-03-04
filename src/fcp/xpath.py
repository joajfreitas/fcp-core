"""Query utility for the Fcp tree structure."""

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

from typing_extensions import Self


class Xpath:
    """Query for the Fcp tree structure.

    Text representation looks like: DataType:field1/field2/field3
    """

    def __init__(self, xpath: str) -> None:
        root, path = xpath.split(":")
        self.root = root
        self.path = path.split("/")

    def append(self, path: str) -> None:
        """Add node to query."""
        self.path.append(path)

    def __truediv__(self, other: Self) -> None:
        if not isinstance(other, str):
            raise TypeError("Expected str")

        self.path.append(other)

    def __str__(self) -> str:
        return f"{self.root}:{'/'.join(self.path)}"
