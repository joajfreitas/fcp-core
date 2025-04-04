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

from beartype.typing import List, Any, Generator, Tuple, Optional
import marko
from marko.block import FencedCode
import pytest
from pathlib import Path
import os
import itertools

from docutils.core import publish_doctree  # type: ignore

from fcp.v2_parser import get_fcp


def get_markdown_fcp_code_blocks(filename: str) -> List[str]:
    with open(filename) as f:
        md = marko.parse(f.read())

    code_blocks = []
    for element in md.children:
        if isinstance(element, FencedCode):
            if element.lang == "fcp":
                code_blocks.append((filename, str(element.children[0].children)))

    return code_blocks


def get_rst_code_blocks(filename: str, language: Optional[str] = None) -> List[str]:
    with open(filename, encoding="utf-8") as file:
        doctree = publish_doctree(file.read())

    def is_code_block(node: Any) -> bool:
        return (
            node.tagname == "literal_block"
            and "code" in node.attributes["classes"]
            and (language in node.attributes["classes"])
            if language is not None
            else True
        )

    code_blocks = doctree.findall(condition=is_code_block)
    source_code = [block.rawsource for block in code_blocks]

    return [(filename, block) for block in source_code]


def get_rst_files(directory: str) -> Generator[Tuple[str, str], None, None]:
    root = Path(directory)
    for path in os.listdir(directory):
        filename = root / path
        if filename.is_file() and filename.suffix == ".rst":
            for _, code_block in get_rst_code_blocks(
                str(filename), "protobuf"
            ):  # protobuf? using fcp would fail the documentation build. TODO: implement fcp syntax for rst
                yield (str(filename), code_block)


@pytest.mark.parametrize(
    "filename, fcp_code_block",
    get_markdown_fcp_code_blocks("README.md")
    + get_markdown_fcp_code_blocks("plugins/fcp_dbc/README.md"),
)  # type: ignore
def test_readme(filename: str, fcp_code_block: str) -> None:
    tmp_name = f"/tmp/{Path(filename).name}.fcp"
    with open(tmp_name, "w") as fp:
        fp.write(fcp_code_block)

    get_fcp(Path(tmp_name)).unwrap()


@pytest.mark.parametrize(
    "filename, fcp_code_block", list(get_rst_files("docs"))
)  # type: ignore
def test_rst(filename: str, fcp_code_block: str) -> None:
    tmp_name = f"/tmp/{Path(filename).name}.fcp"
    with open(tmp_name, "w") as fp:
        fp.write(fcp_code_block)

    get_fcp(Path(tmp_name)).unwrap()


def test_source_files_structure() -> None:
    code_blocks = get_rst_code_blocks("docs/hacking.rst", "bash")

    code_blocks = [block for _, block in code_blocks]

    for _, _, file_names in os.walk("src/fcp"):
        for file_name in file_names:
            if os.path.splitext(file_name)[1] == ".py":
                assert (
                    file_name in code_blocks[1]
                ), f"Couldn't find file {file_name} in docs/hacking.rst"


def test_dir_tree_structure() -> None:
    code_blocks = get_rst_code_blocks("docs/hacking.rst", "bash")

    code_blocks = [block for _, block in code_blocks]

    for dirpath, dirs, _ in itertools.chain(os.walk("src"), os.walk("plugins")):
        for dir in dirs:
            if (
                dir.startswith(".")
                or dir.startswith("_")
                or dir in ["__pycache__", "generated_code", "cache"]
            ):
                continue

            assert (
                dir in code_blocks[0]
            ), f"Couldn't find directory {dirpath}/{dir} in docs/hacking.rst"
