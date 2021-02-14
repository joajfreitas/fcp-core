import pytest

from hypothesis import given
import hypothesis.strategies as st

from ...specs import Signal, SignalValueError
from ..test_spec import spec, json

from .test_message import message, device

from ...can import CANMessage


@pytest.fixture(scope="session")
def signal(message):
    return Signal(parent=message, start=0, length=16, scale=1, offset=0)


def test_signal_encode(signal):
    assert signal.encode(10) == 10

def test_signal_encode_scale(signal):
    signal.scale = 0.1
    assert signal.encode(10) == 100

def test_signal_encode_offset(signal):
    signal.scale = 10
    signal.offset = 50
    assert signal.encode(150) == 10
    signal.scale = 1
    signal.offset = 0

@given(s = st.integers(min_value=0))
def test_decode_signal_encode(signal, s):
    try:
        data64 = signal.encode(s)
        return
    except SignalValueError:
        return
    msg = CANMessage(sid=1, dlc=8, data64=data64, timestamp=0)
    assert signal.decode(msg) == s
