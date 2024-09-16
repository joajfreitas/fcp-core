import pytest
import os
import json
from typing import Any

from fcp.v2_parser import get_fcp
from serde.se import to_dict

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

from pprint import pprint

@pytest.mark.parametrize(
    "test_name", ["001_basic_struct", "002_basic_enum", "003_comments"]
)  # type: ignore
def test_parser(test_name: str) -> None:
    config_dir = os.path.join(THIS_DIR, "configs")
    fcp_config = os.path.join(config_dir, test_name + ".fcp")
    result_path = os.path.join(config_dir, test_name + ".json")

    fcp_v2, sources = get_fcp(fcp_config).unwrap()

    fcp_json_dict = fcp_v2.unwrap().to_dict()

    # Load the expected json result
    with open(result_path, "r") as result_file:
        expected_result_dict = json.dumps(json.load(result_file), indent=2)

    assert fcp_json_dict == expected_result_dict
