import os
from pathlib import Path
from fcp.lib import encode
from fcp.specs.v2 import FcpV2
from fcp.v2_parser import get_fcp

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def get_fcp_config(scope: str, name: str) -> Path:
    config_dir = os.path.join(THIS_DIR, "schemas", scope)
    return Path(os.path.join(config_dir, name + ".fcp"))


def test_encode_simple_struct():
    fcp, _ = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

    assert encode(fcp, "foo", {"bar": 1}) == bytearray([1])

    assert False
