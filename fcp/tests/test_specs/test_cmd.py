import pytest

from ...specs import *
from ...can import CANMessage

from ..test_spec import spec, json

@pytest.fixture
def common():
    return Common()

@pytest.fixture
def send_cmd(common):
    msg = Message(parent=common)
    common.msgs["send_cmd"] = msg
    return msg

@pytest.fixture
def cmd(spec):
    devs = list(spec.devices.values())
    return Command(parent=devs[0])

def test_cmd_encode(send_cmd, cmd):
    """test encode of send cmd"""
    args = [1,2,3]
    msg = cmd.encode(1, 10, args)

    assert type(msg) is CANMessage
    datas = msg.get_data16()
    assert datas[1] == args[0]
    assert datas[2] == args[1]
    assert datas[3] == args[2]

def test_cmd_is_cmd(cmd, common):
    args=[1,2,3]
    msg = cmd.encode(1,10,args)
    assert cmd.is_cmd(msg)
    msg = CANMessage(sid=63<<5, dlc=8, data16=[1,2,3,4], timestamp=0)
    assert not cmd.is_cmd(msg)


