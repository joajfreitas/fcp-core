import json
from fcp.spec import *
from fcp.can import CANMessage

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

    def encode_msg(self, sid: int, msg_name: str, signals: Dict[str, float]) -> CANMessage:
        msg = self.messages.get(msg_name)

        data = 0

        sigs = msg.signals

        for name, value in signals.items():
            signal = sigs[name]
            data |= encode_signal(signal, value)

        sid = make_sid(sid, msg.id)
        return CANMessage(sid, msg.dlc, 1, data64 = data)

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
    
    def find_device(self, id):
        for dev in self.spec.devices.values:
            if isinstance(id, int) and dev.id == id:
                return dev
            if isinstance(id, str) and dev.name == id:
                return dev

        return None

    def find_config(self, dev, id):
        for name, cfg in dev.cfgs.items():
            if isinstance(id, str) and name == id:
                return cfg

        return None


    def decode_msg(self, msg: CANMessage):
        fcp_msg = self.find_msg(msg)
        if fcp_msg == None:
            return "", {}

        signals = {}
        data = 0
        for i, d in enumerate(msg.get_data16()):
            data += d << 16 * i

        for name, signal in fcp_msg.signals.items():
            signals[name] = decode_signal(signal, data)

        return fcp_msg.name, signals

    def decode_log(self, signal):
        for name, log in self.spec.logs.items():
            if log.id == signal["id"]:
                return log.string

        return ""

    def decode_get(self, signal):
        dev = self.find_device(signal['dst'])
        if dev == None:
            return None

        for name, config in dev.cfgs.items():
            if config.id == signal['id']:
                return {config.name : signal['data']}

    
    def encode_get(self, sid: int, dst: int, config: int):
        return encode_msg(sid, "req_get", {"dst": dst, "id": config})

    def decode_set(self, signal):
        dev = self.find_device(signal['dst'])
        if dev == None:
            return None

        for name, config in dev.cfgs.items():
            if config.id == signal['id']:
                return {"device": device.name, config.name : signal['data']}

    
    def encode_set(self, sid: int, dst: int, config: int, value: int):
        return encode_msg(sid, "req_set", {"dst": dst, "id": config, "value": value})

#class FCPCom():
#    def __init__(self, fcp, com, sid):
#        self.fcp = fcp
#        self.com = com
#        self.sid = sid
#
#    def get(self, device, config):
#        dev = self.fcp.find_device(device)
#        if dev == None:
#            return None
#
#        cfg = self.fcp.find_config(dev, config)
#        if cfg == None:
#            return None
#
#        msg = self.fcp.encode_get(self.sid, dev.id, cfg.id)
#
#        com.send(msg)




