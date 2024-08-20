import pytest

#from fcp.specs import Broadcast, Struct, Signal, BroadcastSignal
#from fcp.result import Ok, Error
#from .generator import message_allocation
#
#
#def make_struct(signals):
#    return Struct(
#        name="test_struct",
#        signals=[
#            Signal(name=f"signal{i}", type=signal[0])
#            for i, signal in enumerate(signals)
#        ],
#    )
#
#
#def make_broadcast(signals):
#    return Broadcast(
#        name="test_broadcast",
#        field={"type": "test_struct"},
#        signals=[
#            BroadcastSignal(
#                name=f"signal{i}",
#                field={} if signal[1] is None else {"start": signal[1]},
#            )
#            for i, signal in enumerate(signals)
#        ],
#    )
#
#
#@pytest.mark.parametrize(
#    "signals,expected",
#    [
#        (
#            [("u16", None), ("u16", None), ("u16", None)],
#            Ok([(0, 16), (16, 16), (32, 16)]),
#        ),
#        (
#            [("u16", None), ("u32", 32), ("u16", None)],
#            Error("Message allocation failed"),
#        ),
#    ],
#)
#def test_message_allocation(signals, expected):
#    struct = make_struct(signals)
#    broadcast = make_broadcast(signals)
#
#    allocation = message_allocation(struct, broadcast)
#    assert allocation == expected
