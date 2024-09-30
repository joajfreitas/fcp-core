from beartype.typing import List
import marko
from marko.block import FencedCode
import pytest
from pathlib import Path

from fcp.v2_parser import get_fcp


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
def test_readme(filename: str, fcp_code_block: str):
    tmp_name = f"/tmp/{Path(filename).name}.fcp"
    with open(tmp_name, "w") as fp:
        fp.write(fcp_code_block)

    fcp_v2, _ = get_fcp(Path(tmp_name)).unwrap()
