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
import os
import json
import re
from pathlib import Path

from fcp.v2_parser import get_fcp
from fcp.specs.v2 import FcpV2
from fcp.verifier import make_general_verifier
from fcp.types import NoReturn
from fcp.error_logger import ErrorLogger

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def get_fcp_config(scope: str, name: str) -> Path:
    config_dir = os.path.join(THIS_DIR, "schemas", scope)
    return Path(os.path.join(config_dir, name + ".fcp"))


def get_result_json(scope: str, name: str) -> FcpV2:
    config_dir = os.path.join(THIS_DIR, "schemas", scope)
    result_path = os.path.join(config_dir, name + ".json")

    with open(result_path, "r") as result_file:
        return json.load(result_file)


def get_result_txt(scope: str, name: str) -> str:
    config_dir = os.path.join(THIS_DIR, "schemas", scope)
    result_path = os.path.join(config_dir, name + ".txt")

    with open(result_path, "r") as result_file:
        return result_file.read()


@pytest.mark.parametrize(
    "test_name",
    [
        "001_basic_struct",
        "002_basic_enum",
        "003_comments",
        "004_struct_composition",
        "005_extends",
        "006_basic_service",
        "007_simple_array_type",
        "008_dynamic_array",
        "009_optional",
        "010_device",
        "011_device_services",
    ],
)  # type: ignore
def test_parser(test_name: str) -> NoReturn:
    fcp_v2, _ = get_fcp(Path(get_fcp_config("syntax", test_name))).unwrap()
    fcp_json_dict = fcp_v2.to_dict()
    expected_result_dict = get_result_json("syntax", test_name)

    assert fcp_json_dict == expected_result_dict


@pytest.mark.parametrize(
    "test_name",
    [
        "001_missing_version",
        "002_wrong_version",
    ],
)  # type: ignore
def test_parsing_errors(test_name: str) -> NoReturn:
    error_logger = ErrorLogger({}, enable_file_paths=False)
    fcp_config = Path(get_fcp_config("error", test_name))
    fcp = get_fcp(fcp_config, error_logger)
    result = get_result_txt("error", test_name)
    assert fcp.is_err()
    assert fcp.err().to_str(source_file_tag=False) == result[:-1]


def test_verifier_no_error() -> NoReturn:
    fcp_v2, _ = get_fcp(get_fcp_config("verifier", "000_no_error")).unwrap()

    verifier = make_general_verifier()
    result = verifier.verify(fcp_v2)
    assert result.is_ok()


@pytest.mark.parametrize(
    "test_name",
    [
        "001_duplicate_types",
        "002_duplicate_impls",
        "003_duplicate_signals",
        "004_duplicate_enumeration_names",
        "005_duplicate_enumeration_values",
    ],
)  # type: ignore
def test_verifier_errors(test_name: str) -> NoReturn:
    fcp_v2, _ = get_fcp(get_fcp_config("verifier", test_name)).unwrap()

    verifier = make_general_verifier()
    assert verifier.verify(fcp_v2).is_err()
