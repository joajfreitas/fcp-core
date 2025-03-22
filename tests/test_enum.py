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

# ruff: noqa: D103 D100

import pytest
from beartype.typing import List, Tuple

from fcp.specs.enum import Enum, Enumeration


@pytest.mark.parametrize(
    "enumeration, expected",
    [
        ([("S1", 0), ("S2", 1), ("S3", 2)], 2),
        ([("S1", 0)], 1),
        ([("S1", 0), ("S2", 1)], 1),
        ([("S1", 0), ("S2", 7)], 3),
        ([("S1", 0), ("S2", 8)], 4),
        ([("S1", 0), ("S2", 255)], 8),
        ([("S1", 0), ("S2", 256)], 9),
    ],
)  # type: ignore
def test_enum_size(enumeration: List[Tuple[str, int]], expected: int) -> None:
    e = Enum(
        name="E",
        enumeration=[Enumeration(name, value, None) for name, value in enumeration],
        meta=None,
    )

    assert e.get_packed_size() == expected
