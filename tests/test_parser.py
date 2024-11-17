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
    ],
)  # type: ignore
def test_parsing_errors(test_name: str) -> NoReturn:
    fcp_config = Path(get_fcp_config("error", test_name))
    fcp = get_fcp(fcp_config)
    result = (
        get_result_txt("error", test_name)
        .replace("    ", "\t")
        .replace("{filename}", fcp_config.name)
    )

    assert fcp.is_err()

    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    # Remove full path (user dependant) from message and keep only the error and file
    error = ansi_escape.sub("", str(fcp.err())).split("/")
    error = error[0] + error[-1]  # type: ignore

    assert error == result  # type: ignore


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
