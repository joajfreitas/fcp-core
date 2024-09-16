import pytest
import os
import json
from pprint import pprint

from fcp.v2_parser import get_fcp
from fcp.v2 import default_serialization

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.parametrize(
    "test_name",
    ["001_basic_struct", "002_basic_enum", "003_comments", "004_struct_composition"],
) # type: ignore
def test_parser(test_name: str) -> None:
    config_dir = os.path.join(THIS_DIR, "configs")
    fcp_config = os.path.join(config_dir, test_name + ".fcp")
    result_path = os.path.join(config_dir, test_name + ".json")

<<<<<<< HEAD
    fcp_v2, sources = get_fcp(fcp_config).unwrap()
=======
    fcp_v2, _ = get_fcp(fcp_config, fpi_config).unwrap()
>>>>>>> e6e4a6b (wip)

    fcp_json_dict = fcp_v2.unwrap().to_dict()

    # Load the expected json result
    with open(result_path, "r") as result_file:
        expected_result_dict = json.dumps(json.load(result_file), indent=2)

    assert fcp_json_dict == expected_result_dict
    #assert 1 == 2

def test_default_serialization():
    config_dir = os.path.join(THIS_DIR, "configs")
    fpi_config = os.path.join(config_dir, "test.fpi")
    fcp_config = os.path.join(config_dir, "004_struct_composition.fcp")

    fcp_v2, _ = get_fcp(fcp_config, fpi_config).unwrap()

    default_serialization(fcp_v2, {})
