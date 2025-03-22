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

import re
import pytest
from pathlib import Path
import os

from beartype.typing import List, Generator


def recursively_search_files(
    extension: str, directory: str, excluded: List[str] = []
) -> Generator[Path, None, None]:
    root = Path(directory)
    for filename in root.rglob("*." + extension):
        if filename.name in excluded:
            continue
        if filename.is_file() and "".join(filename.suffixes) == "." + extension:
            yield filename


def param_name(path: Path) -> str:
    return str(path)


def check_license(license_regex: re.Pattern, filename: Path) -> None:
    with open(filename) as f:
        contents = f.read()

    assert (
        len(license_regex.findall(contents)) == 1
    ), f"{filename} does not contain a license notice"


@pytest.mark.parametrize(
    "filename",
    list(recursively_search_files("py", "src", excluded=["result.py", "maybe.py"]))
    + list(recursively_search_files("py", "plugins"))
    + list(recursively_search_files("py", "tests")),
    ids=param_name,
)  # type: ignore
def test_python_license_notice_is_present(filename: Path) -> None:
    check_license(
        re.compile(r"^# Copyright \(c\) 20\d\d the fcp AUTHORS\.\n"), filename
    )


@pytest.mark.parametrize(
    "filename",
    list(recursively_search_files("h.j2", "plugins/fcp_cpp"))
    + list(recursively_search_files("cpp.j2", "plugins/fcp_cpp")),
    ids=param_name,
)  # type: ignore
def test_jinja_templates_license_notice_is_present(filename: Path) -> None:
    check_license(
        re.compile(r"^\/\/ Copyright \(c\) 20\d\d the fcp AUTHORS\.\n"), filename
    )


@pytest.mark.parametrize(
    "filename",
    list(recursively_search_files("cpp", "plugins/fcp_cpp"))
    + list(recursively_search_files("h", "plugins/fcp_cpp")),
    ids=param_name,
)  # type: ignore
def test_cpp_license_notice_is_present(filename: Path) -> None:
    check_license(
        re.compile(r"^\/\/ Copyright \(c\) 20\d\d the fcp AUTHORS\.\n"), filename
    )
