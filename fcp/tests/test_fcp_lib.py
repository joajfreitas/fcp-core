import pytest

from ..fcp_lib import *
from ..can import CANMessage

@pytest.fixture
def fcp():
    with open("json/test.json") as f:
        j = json.loads(f.read())

    spec = Spec()
    spec.decompile(j)
    return Fcp(spec)

@pytest.fixture
def test_msg(fcp):
    return fcp.encode_msg("iib_motor", {"temp_motor":10})

def test_encode_msg(fcp, test_msg):
    msg = fcp.encode_msg("iib_motor", {"temp_motor":10})
    assert type(msg) is CANMessage
    assert msg.get_dev_id() == 16

def test_decode_msg(fcp, test_msg):
    name, signals = fcp.decode_msg(test_msg)
    assert name == "iib_motor"
    assert signals["temp_motor0"] == 10

def test_encode_cmd(fcp):
    msg = fcp.encode_cmd(10, "iib", "set_regen_on", [1,2,3])
    assert msg is not None

class FakeProxy():
    def __init__(self, socket, addrs):
        self.socket = socket
        self.addrs = []
        self.i = 0

    def recv(self) -> CANMessage:
        msgs = [
            CANMessage(sid=80, dlc=8, data16=[8<<8,2,0,0], timestamp=0),
            CANMessage(sid=208, dlc=8, data16=[1,1,0,0], timestamp=0),
            CANMessage(sid=144, dlc=8, data16=[1,1,0,0], timestamp=0)
        ]

        msg = msgs[self.i]
        self.i = (self.i + 1) % len(msgs)
        return Ok(msg)

    def send(self, msg: CANMessage):
        return

@pytest.fixture
def fcpcom(fcp):
    fcp_com = FcpCom(fcp, FakeProxy(None, None))
    return fcp_com

def test_fcpcom_cmd(fcpcom):
    fcpcom.start()
    rets = fcpcom.cmd("iib", "add", (1,1,0))
    fcpcom.stop()
    print(rets)
    assert rets.is_ok()
    assert rets.unwrap()[0] == 2

def test_fcpcom_set(fcpcom):
    fcpcom.start()
    rets = fcpcom.set("iib", "regen_on", 1)
    fcpcom.stop()
    print(rets)
    assert rets.is_ok()

def test_fcpcom_get(fcpcom):
    fcpcom.start()
    rets = fcpcom.get("iib", "regen_on")
    fcpcom.stop()
    print(rets)
    assert rets.is_ok()
    assert rets.unwrap() == 1

#def test_decode_msg(fcp):
#    msg = CANMessage(1232, 8, 0, data16=[0,0,0,0])
#    msg, signals = fcp.decode_msg(msg)
#    assert "motor_speed0" in signals.keys()
#    assert "n_motor_info" in signals.keys()
