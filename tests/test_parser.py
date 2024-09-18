from fcp.specs.v2 import FcpV2
import pytest
import os
import json

from serde import from_dict
from serde.json import to_json

from fcp.v2_parser import get_fcp

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.parametrize("test_name", ["001"])
def test_parser(test_name):
    config_dir = os.path.join(THIS_DIR, "configs")
    fcp_config = os.path.join(config_dir, test_name + ".fcp")
    result_path = os.path.join(config_dir, test_name + ".json")

    fcp_v2, sources = get_fcp(fcp_config).unwrap()

    # Convert FcpV2 object to JSON string and then to a dictionary
    fcp_json_dict = json.loads(to_json(from_dict(FcpV2, fcp_v2.unwrap())))

    # Load the expected JSON result as a dictionary to compare with the generated JSON
    with open(result_path, "r") as result_file:
        expected_result_dict = json.load(result_file)

    assert fcp_json_dict == expected_result_dict
