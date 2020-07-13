import json
from fcp.spec import *
from fst_cantools import Message as CANmessage

from math import *


def bitmask(n):
    return 2 ** n - 1

def test_bitmask():
    assert 0xF == bitmask(4)


def encode_signal(signal, value):
    value = (value - signal.offset) / signal.scale
    return (int(value) & bitmask(signal.length)) << signal.start


def conv_endianess(value: int, signal: Signal):
    length = signal.get_length()/8
    log2_length = log2(length)
    
    if length == 1:
        return value

    if log2_length != int(log2_length):
        return value

    if signal.get_byte_order() != "big_endian":
        return value

    length = int(length)
    def swap64(x):
        return int.from_bytes(value.to_bytes(8, byteorder='little'), byteorder='big', signed=False)
    def swap32(x):
        return int.from_bytes(value.to_bytes(4, byteorder='little'), byteorder='big', signed=False)
    def swap16(x):
        return int.from_bytes(value.to_bytes(2, byteorder='little'), byteorder='big', signed=False)

    if length == 8:
        return swap64(value)
    if length == 4:
        return swap32(value) 
    if length == 2:
        return swap16(value)


def decode_signal(signal, value):
    value = (value >> signal.start) & bitmask(signal.length)
    value = conv_endianess(value, signal)
    if signal.type == 'signed':
        value = int(value)
        if (value >> (signal.length - 1)) == 1:
            value = - ((value ^ bitmask(signal.length)) + 1)
    return (value * signal.scale) + signal.offset


class Fcp:
    def __init__(self, spec):
        self.messages = {}
        self.spec = spec

        for device in spec.devices.values():
            for msg in device.msgs.values():
                self.messages[msg.name] = msg

        for msg in spec.common.msgs.values():
            self.messages[msg.name] = msg

    def encode_msg(self, sid, msg_name, signals):
        msg = self.messages.get(msg_name)

        data = 0

        sigs = msg.signals

        for name, value in signals.items():
            signal = sigs[name]
            data |= encode_signal(signal, value)

        datas = [0, 0, 0, 0]
        for i in range(4):
            datas[i] = (data >> 16 * i) & 0xFFFF

        sid = make_sid(sid, msg.id)
        return CANmessage(sid, msg.dlc, datas, 1)

    def find_msg(self, msg):
        dev_id, msg_id = decompose_id(msg.sid)

        for dev in self.spec.devices.values():
            if dev.id == dev_id:
                for msg in dev.msgs.values():
                    if msg.id == msg_id:
                        return msg

        for msg in self.spec.common.msgs.values():
            if msg.id == msg_id:
                return msg

    def decode_msg(self, msg):
        fcp_msg = self.find_msg(msg)
        if fcp_msg == None:
            return "", {}

        signals = {}
        data = 0
        for i, d in enumerate(msg.data):
            data += d << 16 * i

        for name, signal in fcp_msg.signals.items():
            signals[name] = decode_signal(signal, data)

        return fcp_msg.name, signals
