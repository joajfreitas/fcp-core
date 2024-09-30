from beartype.typing import List, Any, Generator, Tuple
import marko
from marko.block import FencedCode
import pytest
from pathlib import Path
import os

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


def get_rst_fcp_code_blocks(filename: str) -> List[str]:

    with open(filename, encoding="utf-8") as file:
        doctree = publish_doctree(file.read())

    def is_code_block(node: Any) -> bool:
        return (
            node.tagname == "literal_block"
            and "code" in node.attributes["classes"]
            and "protobuf" in node.attributes["classes"]
        )

    code_blocks = doctree.findall(condition=is_code_block)
    source_code = [block.rawsource for block in code_blocks]

    return [(filename, block) for block in source_code]


def get_rst_files(directory: str) -> Generator[Tuple[str, str], None, None]:
    root = Path(directory)
    for path in os.listdir(directory):
        filename = root / path
        if filename.is_file() and filename.suffix == ".rst":
            for _, code_block in get_rst_fcp_code_blocks(str(filename)):
                yield (str(filename), code_block)


@pytest.mark.parametrize(
    "filename, fcp_code_block",
    get_markdown_fcp_code_blocks("README.md")
    + get_markdown_fcp_code_blocks("plugins/fcp_dbc/README.md"),
)  # type: ignore
def test_readme(filename: str, fcp_code_block: str):
    tmp_name = f"/tmp/{Path(filename).name}.fcp"
    with open(tmp_name, "w") as fp:
        fp.write(fcp_code_block)

    fcp_v2, _ = get_fcp(Path(tmp_name)).unwrap()


@pytest.mark.parametrize(
    "filename, fcp_code_block", list(get_rst_files("docs"))
)  # type: ignore
def test_rst(filename: str, fcp_code_block: str):
    tmp_name = f"/tmp/{Path(filename).name}.fcp"
    with open(tmp_name, "w") as fp:
        fp.write(fcp_code_block)

    fcp_v2, _ = get_fcp(Path(tmp_name)).unwrap()
