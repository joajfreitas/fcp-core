# ruff: noqa: D103 D100

import re
import pytest
from pathlib import Path
import os

from beartype.typing import List, Generator


def get_python_files(
    directory: str, excluded: List[str] = []
) -> Generator[Path, None, None]:
    root = Path(directory)
    for filename in root.rglob("*.py"):
        if filename.name in excluded:
            continue
        if filename.is_file() and filename.suffix == ".py":
            yield filename


def param_name(path: Path) -> str:
    return str(path)


@pytest.mark.parametrize(
    "filename",
    list(get_python_files("src", excluded=["result.py", "maybe.py"]))
    + list(get_python_files("plugins")),
    ids=param_name,
)  # type: ignore
def test_license_notice_is_present(filename: Path) -> None:
    print(filename)
    license_regex = re.compile(
        r"^# Copyright \(c\) 20\d\d the fcp AUTHORS\.\n#\n# Permission is hereby granted, free of charge, to any person obtaining a copy\n# of this software and associated documentation files \(the \"Software\"\), to deal\n# in the Software without restriction, including without limitation the rights\n# to use, copy, modify, merge, publish, distribute, sublicense, and\/or sell\n# copies of the Software, and to permit persons to whom the Software is\n# furnished to do so, subject to the following conditions:\n#\n# The above copyright notice and this permission notice shall be included in all\n# copies or substantial portions of the Software.\n#\n# THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n# SOFTWARE.\n"
    )
    with open(filename) as f:
        contents = f.read()

    assert len(license_regex.findall(contents)) == 1
