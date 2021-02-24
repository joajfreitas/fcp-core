import pytest

from ...specs import *
from ...can import CANMessage

@pytest.fixture(scope="session")
def device():
    spec = Spec()
    dev = Device(parent = spec)
    return dev

@pytest.fixture(scope="session")
def message(device):
    msg = Message(parent = device, id=1)
    msg.add_signal(Signal(parent=msg, name="test1", start=0, length=8))
    msg.add_signal(Signal(parent=msg, name="test5", start=8, length=8))
    msg.add_signal(Signal(parent=msg, name="test2", start=16, length=16))
    msg.add_signal(Signal(parent=msg, name="test3", start=32, length=16))
    msg.add_signal(Signal(parent=msg, name="test4", start=48, length=16))
    return msg

#@pytest.fixture(scope="session")

def test_encode(message):
    msg = message.encode({"test1": 10, "test5": 10})
    assert type(msg) is CANMessage
    print(msg)
    assert msg.get_data16()[0] == 2570

#def test_decode(message, can_msg):
#    
