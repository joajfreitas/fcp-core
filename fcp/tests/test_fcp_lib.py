from ..fcp_lib import *
import pytest

@pytest.fixture
def fcp():
    with open("json/fst10e.json") as f:
        j = json.loads(f.read())

    spec = Spec()
    spec.decompile(j)
    return Fcp(spec)

def test_decode_msg(fcp):
    msg = CANMessage(1232, 8, 0, data16=[0,0,0,0])
    msg, signals = fcp.decode_msg(msg)
    assert "motor_speed0" in signals.keys()
    assert "n_motor_info" in signals.keys()
