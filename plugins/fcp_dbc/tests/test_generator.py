import os
import pytest
from pathlib import Path

from fcp_dbc import Generator

from fcp.v2_parser import get_fcp

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def get_fcp_config(name: str) -> str:
    config_dir = os.path.join(THIS_DIR, "configs")
    return os.path.join(config_dir, name + ".fcp")


def get_result_dbc(name: str) -> str:
    config_dir = os.path.join(THIS_DIR, "configs")
    result_path = os.path.join(config_dir, name + ".dbc")

    with open(result_path, "r") as result_file:
        return result_file.read()


def get_bo(dbc: str) -> str:
    sections = [section for section in dbc.split("\r\n") if section != ""]

    bo_sections = [
        section
        for section in sections
        if section.startswith("BO_") or section.startswith(" SG_")
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
    ],
)  # type: ignore
def test_dbc_generator(test_name: str) -> None:
    fcp_v2, _ = get_fcp(Path(get_fcp_config(test_name))).unwrap()
    dbc = get_result_dbc(test_name)
    generator = Generator()

    results = generator.generate(
        fcp_v2,
        {"output": "output.dbc"},
    )
    result = get_bo(results[0].get("contents"))

    print(result)
    print(dbc)
    assert result == dbc
