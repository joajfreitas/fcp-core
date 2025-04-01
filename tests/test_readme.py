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

from beartype.typing import List
import marko
from marko.block import FencedCode
import pytest
from pathlib import Path

from fcp.parser import get_fcp


def get_fcp_code_blocks(filename: str) -> List[str]:
    with open(filename) as f:
        md = marko.parse(f.read())

    code_blocks = []
    for element in md.children:
        if isinstance(element, FencedCode):
            if element.lang == "fcp":
                code_blocks.append((filename, str(element.children[0].children)))

    return code_blocks


@pytest.mark.parametrize(
    "filename, fcp_code_block",
    get_fcp_code_blocks("README.md") + get_fcp_code_blocks("plugins/fcp_dbc/README.md"),
)  # type: ignore
def test_readme(filename: str, fcp_code_block: str) -> None:
    tmp_name = f"/tmp/{Path(filename).name}.fcp"
    with open(tmp_name, "w") as fp:
        fp.write(fcp_code_block)

    get_fcp(Path(tmp_name)).unwrap()


def test_example() -> None:
    get_fcp(Path("example/example.fcp")).unwrap()
