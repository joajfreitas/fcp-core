import pytest
import os
import json

from fcp.v2_parser import get_fcp

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

@pytest.mark.parametrize("fcp,result", [("001.fcp", "001.json")])
def test_parser(fcp, result):
    config_dir = os.path.join(THIS_DIR, "configs")
    print("config dir", config_dir)
    fpi_config = os.path.join(config_dir, "test.fpi")
    fcp_config = os.path.join(config_dir, fcp)
    result = os.path.join(config_dir, result)

    fcp_v2, sources = get_fcp(fcp_config, fpi_config).unwrap()
   
    fcp_json = fcp_v2.unwrap().to_dict()
    result = json.loads(open(result).read())
    

    assert fcp_json == result
