import pytest
import os
import json

from fcp.v2_parser import get_fcp

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.parametrize("test_name", ["001", "002"])
def test_parser(test_name):
    config_dir = os.path.join(THIS_DIR, "configs")
    print("config dir", config_dir)
    fpi_config = os.path.join(config_dir, "test.fpi")
    fcp_config = os.path.join(config_dir, test_name + ".fcp")
    result = os.path.join(config_dir, test_name + ".json")

    fcp_v2, sources = get_fcp(fcp_config, fpi_config).unwrap()

    fcp_json = fcp_v2.unwrap().to_dict()
    result = json.loads(open(result).read())

    assert fcp_json == result
