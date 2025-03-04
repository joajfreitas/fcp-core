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

import os
import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile

from fcp_dbc import Generator
from fcp.v2_parser import get_fcp
from fcp.verifier import make_general_verifier

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def get_fcp_config(dir: str, name: str) -> str:
    config_dir = os.path.join(THIS_DIR, "schemas", dir)
    return os.path.join(config_dir, name + ".fcp")


def get_result_dbc(dir: str, name: str) -> str:
    config_dir = os.path.join(THIS_DIR, "schemas", dir)
    result_path = os.path.join(config_dir, name + ".dbc")

    with open(result_path, "r") as result_file:
        return result_file.read()


def get_bo(dbc: str) -> str:
    sections = [section for section in dbc.split("\r\n") if section != ""]

    bo_sections = [
        section
        for section in sections
        if section.startswith("BO_")
        or section.startswith(" SG_")
        or section.startswith("SG_MUL_VAL_")
    ]

    return "\n".join(bo_sections) + "\n"


@pytest.mark.parametrize(
    "test_name",
    [
        "001_basic_struct",
        "002_nested_enum",
        "003_nested_struct",
        "004_nested_nested_struct",
        "005_small_types",
        "006_big_endian",
        "007_muxed_signals",
        "008_simple_array",
        "009_compounded_type_array",
        "010_multiple_bus",
    ],
)  # type: ignore
def test_dbc_generator(test_name: str) -> None:
    fcp_v2, _ = get_fcp(Path(get_fcp_config("generator", test_name))).unwrap()
    generator = Generator()

    results = generator.generate(
        fcp_v2,
        {"output": "output"},
    )

    for result in results:
        contents = get_bo(result.get("contents"))
        dbc = get_result_dbc("generator", test_name + "_" + result.get("bus"))

        assert contents == dbc


def test_verifier_no_error() -> None:
    fcp_v2, _ = get_fcp(Path(get_fcp_config("verifier", "000_no_error"))).unwrap()

    verifier = make_general_verifier()
    generator = Generator()
    generator.register_checks(verifier)

    assert verifier.verify(fcp_v2).is_ok()


@pytest.mark.parametrize(
    "test_name",
    [
        "001_duplicate_ids",
    ],
)  # type: ignore
def test_verifier(test_name: str) -> None:
    fcp_v2, _ = get_fcp(Path(get_fcp_config("verifier", test_name))).unwrap()

    verifier = make_general_verifier()
    generator = Generator()
    generator.register_checks(verifier)

    assert verifier.verify(fcp_v2).is_err()


def test_encoding_message_to_big() -> None:
    tmp = NamedTemporaryFile()
    with open(tmp.name, "w") as fp:
        fp.write(
            """
version: "3"

struct Foo {
    s1 @0: u32,
    s2 @1: u32,
    s3 @2: u8,
}

impl can for Foo {
    id: 10,
}"""
        )

    fcp_v2, _ = get_fcp(tmp.name).unwrap()
    generator = Generator()

    with pytest.raises(ValueError):
        generator.generate(fcp_v2, {"output": "output.dbc"})
