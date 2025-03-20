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
        if filename.is_file() and filename.suffix == "." + extension:
            yield filename


def param_name(path: Path) -> str:
    return str(path)


def check_license(license_regex, filename):
    with open(filename) as f:
        contents = f.read()

    assert (
        len(license_regex.findall(contents)) == 1
    ), f"{filename} does not contain a license notice"


@pytest.mark.parametrize(
    "filename",
    list(recursively_search_files("py", "src", excluded=["result.py", "maybe.py"]))
    + list(recursively_search_files("py", "plugins")),
    ids=param_name,
)  # type: ignore
def test_python_license_notice_is_present(filename: Path) -> None:
    check_license(
        re.compile(r"^# Copyright \(c\) 20\d\d the fcp AUTHORS\.\n"), filename
    )


@pytest.mark.parametrize(
    "filename", list(recursively_search_files("j2", ".")), ids=param_name
)
def test_jinja_templates_license_notice_is_present(filename: Path):
    check_license(
        re.compile(r"^\/\/ Copyright \(c\) 20\d\d the fcp AUTHORS\.\n"), filename
    )


@pytest.mark.parametrize(
    "filename",
    list(recursively_search_files("cpp", "plugins/fcp_cpp"))
    + list(recursively_search_files("h", "plugins/fcp_cpp")),
    ids=param_name,
)
def test_cpp_license_notice_is_present(filename: Path):
    check_license(
        re.compile(r"^\/\/ Copyright \(c\) 20\d\d the fcp AUTHORS\.\n"), filename
    )
