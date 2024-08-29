from fcp.specs.v2 import FcpV2
import pytest
import os
import json


from serde import from_dict
from fcp.v2_parser import get_fcp

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.parametrize("test_name", ["001", "002"])
def test_parser(test_name):
    config_dir = os.path.join(THIS_DIR, "configs")
    fpi_config = os.path.join(config_dir, "test.fpi")
    fcp_config = os.path.join(config_dir, test_name + ".fcp")
    result = os.path.join(config_dir, test_name + ".json")

    print(">>>", fcp_config)
    fcp_v2, sources = get_fcp(fcp_config, fpi_config).unwrap()

    print(fcp_v2.unwrap())
    fcp_json = from_dict(FcpV2, fcp_v2.unwrap())
    result = json.loads(open(result).read())

    # print(fcp_json)
    # print()
    # print(result)
    assert fcp_json == result
