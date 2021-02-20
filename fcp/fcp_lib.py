import json
from typing import *
from math import *
import queue
from threading import Thread
from result import Ok, Err
import atexit

from fcp.specs import *
from fcp.can import CANMessage


def encode_signal(signal, value):
    value = (value - signal.offset) / signal.scale
    return (int(value) & bitmask(signal.length)) << signal.start


def conv_endianess(value: int, signal: Signal):
    length = signal.length / 8
    log2_length = log2(length)

    if length == 1:
        return value

    if log2_length != int(log2_length):
        return value

    if signal.byte_order != "big_endian":
        return value

    length = int(length)

    def swap64(x):
        return int.from_bytes(
            value.to_bytes(8, byteorder="little"), byteorder="big", signed=False
        )

    def swap32(x):
        return int.from_bytes(
            value.to_bytes(4, byteorder="little"), byteorder="big", signed=False
        )

    def swap16(x):
        return int.from_bytes(
            value.to_bytes(2, byteorder="little"), byteorder="big", signed=False
        )

    if length == 8:
        return swap64(value)
    if length == 4:
        return swap32(value)
    if length == 2:
        return swap16(value)

class Fcp:
    def __init__(self, spec):
        self.messages = {}

        if type(spec) is str:
            with open(spec) as f:
                j = json.loads(f.read())
            spec = Spec()
            spec.decompile(j)
            self.spec = spec
        elif type(spec) is Spec:
            self.spec = spec


        for device in spec.devices.values():
            for msg in device.msgs.values():
                self.messages[msg.name] = msg

        for msg in spec.common.msgs.values():
            self.messages[msg.name] = msg

    def encode_msg(
        self, msg_name: str, signals: Dict[str, float], src: int = None) -> CANMessage:
        msg = self.messages.get(msg_name)
        return msg.encode(signals, src)

    def decode_msg(self, msg: CANMessage):
        fcp_msg = self.find_msg(msg)
        if fcp_msg is None:
            return "", {}

        return fcp_msg.decode(msg)

    def encode_cmd(self, src: int, dst: str, name: str, args) -> CANMessage:
        device = self.find_device(dst)
        if device is None:
            return Err(f"{dst} device not found")

        cmd = device.get_cmd(name)
        if cmd is None:
            return Err(f"{dst}/{name} cmd not found")

        return Ok(cmd.encode(src, device.id, args))

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
        for dev in self.spec.devices.values():
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


    def decode_log(self, signal):
        for name, log in self.spec.logs.items():
            if log.id == signal["id"]:
                return log.string

        return ""

    def decode_get(self, signal):
        dev = self.find_device(signal["dst"])
        if dev == None:
            return None

        for name, config in dev.cfgs.items():
            if config.id == signal["id"]:
                return {config.name: signal["data"]}

    def encode_get(self, src: int, dst: int, config: int):
        device = self.find_device(dst)
        if device is None:
            return Err(f"{dst} device not found")

        cfg = device.get_cfg(config)
        if cfg is None:
            return Err(f"{dst}/{name} cfg not found")

        return Ok(cfg.encode_get(src, device.id))

    def decode_set(self, signal):
        dev = self.find_device(signal["dst"])
        if dev == None:
            return None

        for name, config in dev.cfgs.items():
            if config.id == signal["id"]:
                return {"device": device.name, config.name: signal["data"]}

    def encode_set(self, src: int, dst: str, config: str, value: int):
        device = self.find_device(dst)
        if device is None:
            return Err(f"{dst} device not found")

        cfg = device.get_cfg(config)
        if cfg is None:
            return Err(f"{dst}/{name} cfg not found")

        return Ok(cfg.encode_set(src, device.id, value))

class Proxy():
    def __init__(self, socket, addrs):
        self.socket = socket
        self.addrs = []

        self.cmds = {}

    def recv(self) -> CANMessage:
        msg, addr = self.socket.recvfrom(1024)
        return Ok(CANMessage.decode_json(msg))

    def send(self, msg: CANMessage):
        for addr in self.addrs:
            self.socket.sendto(msg.encode_json(), addr)

class FcpCom():
    def __init__(self, fcp: Fcp, proxy: Proxy, id: int = 31):
        self.fcp = fcp
        self.proxy = proxy
        self.id = id

        self.terminate = False
        self.cmds = {}
        self.sets = {}
        self.gets = {}
        self.q = queue.Queue()

    def start(self):
        self.thread = Thread(target=self.run, daemon=True)
        self.thread.start()

    def stop(self):
        self.terminate = True
        self.thread.join()

    def cmd(self, dst, name, args):
        if self.cmds.get((dst, name)) is None:
            self.cmds[(dst, name)] = queue.Queue()

        msg = self.fcp.encode_cmd(self.id, dst, name, args)
        if msg.is_err():
            return msg
        msg = msg.ok()
        self.proxy.send(msg)

        try:
            r = self.cmds[(dst, name)].get(timeout=2)
            return Ok(r)
        except queue.Empty as e:
            return Err("Timeout")

    def set(self, dst, name, value):
        if self.sets.get((dst, name)) is None:
            self.sets[(dst, name)] = queue.Queue()

        msg = self.fcp.encode_set(self.id, dst, name, value)
        if msg.is_err():
            return msg
        msg = msg.ok()
        self.proxy.send(msg)

        try:
            self.sets[(dst, name)].get(timeout=2)
            return Ok()
        except queue.Empty as e:
            return Err("Timeout")

    def get(self, dst, name):
        if self.gets.get((dst, name)) is None:
            self.gets[(dst, name)] = queue.Queue()

        msg = self.fcp.encode_get(self.id, dst, name)
        if msg.is_err():
            return msg
        msg = msg.ok()
        self.proxy.send(msg)

        try:
            r = self.gets[(dst, name)].get(timeout=2)
            return Ok(r)
        except queue.Empty as e:
            return Err("Timeout")


    def run(self):
        while True:
            if self.terminate == True:
                break
            r = self.proxy.recv()
            if r.is_err():
                continue
            msg = r.ok()
            name, signals = self.fcp.decode_msg(msg)

            self.q.put((name, signals))

            if name == "return_cmd":
                dev = self.fcp.spec.get_device(msg.get_dev_id())
                cmd = dev.get_cmd(signals["id"])
                rets = (signals["ret1"], signals["ret2"], signals["ret3"])
                q = self.cmds.get((dev.name, cmd.name))
                if q is not None:
                    q.put(rets)
            elif name == "ans_set":
                dev = self.fcp.spec.get_device(msg.get_dev_id())
                cfg = dev.get_cfg(signals["id"])
                q = self.sets.get((dev.name, cfg.name))
                if q is not None:
                    q.put(None)
            elif name == "ans_get":
                dev = self.fcp.spec.get_device(msg.get_dev_id())
                cfg = dev.get_cfg(signals["id"])
                ret = signals["data"]
                q = self.gets.get((dev.name, cfg.name))
                if q is not None:
                    q.put(ret)
                pass

