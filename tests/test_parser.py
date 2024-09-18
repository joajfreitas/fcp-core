import pytest
import os
import json
from pprint import pprint
from typing import Any


from fcp.v2_parser import get_fcp

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.parametrize(
    "test_name", ["001_basic_struct", "002_basic_enum", "003_comments"]
)  # type: ignore
def test_parser(test_name: str) -> None:
    def drop_meta(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: drop_meta(v) for k, v in obj.items() if k != "meta"}
        elif isinstance(obj, list):
            return [drop_meta(x) for x in obj]
        else:
            return obj

    config_dir = os.path.join(THIS_DIR, "configs")
    fcp_config = os.path.join(config_dir, test_name + ".fcp")
    result_path = os.path.join(config_dir, test_name + ".json")

    fcp_v2, sources = get_fcp(fcp_config).unwrap()

    # Convert FcpV2 object to dictionary
    fcp_json_dict = drop_meta(fcp_v2.unwrap().to_json())

    # Load the expected json result
    with open(result_path, "r") as result_file:
        expected_result_dict = json.load(result_file)

    pprint(fcp_json_dict)
    pprint(expected_result_dict)
    assert fcp_json_dict == expected_result_dict
