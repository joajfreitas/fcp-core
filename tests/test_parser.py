from fcp.specs.v2 import FcpV2
import pytest
import os
import json

from serde import from_dict
from serde.json import to_json

from fcp.v2_parser import get_fcp

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

from pprint import pprint


@pytest.mark.parametrize("test_name", ["001", "002", "003"])
def test_parser(test_name: str) -> None:
    def drop_meta(obj):
        if isinstance(obj, dict):
            return {k: drop_meta(v) for k, v in obj.items() if k != "meta"}
        elif isinstance(obj, list):
            return [drop_meta(x) for x in obj]
        else:
            return obj

    config_dir = os.path.join(THIS_DIR, "configs")
    fpi_config = os.path.join(config_dir, "test.fpi")
    fcp_config = os.path.join(config_dir, test_name + ".fcp")
    result_path = os.path.join(config_dir, test_name + ".json")

    fcp_v2, sources = get_fcp(fcp_config, fpi_config).unwrap()

    # Convert FcpV2 object to JSON string and then to a dictionary
    fcp_json_dict = drop_meta(fcp_v2.unwrap().to_json())

    # Load the expected JSON result as a dictionary to compare with the generated JSON
    with open(result_path, "r") as result_file:
        expected_result_dict = json.load(result_file)

    pprint(fcp_json_dict)
    pprint(expected_result_dict)
    assert fcp_json_dict == expected_result_dict
