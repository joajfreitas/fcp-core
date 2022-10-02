import logging
import json
from itertools import accumulate
from serde import Model, fields
from fcp.specs.broadcast import Broadcast, BroadcastSignal

from fcp.specs.struct import Struct
from .v2 import FcpV2
from . import Argument, Comment
from .v2 import Device as DeviceV2
from .v2 import Config as ConfigV2
from .v2 import Command as CommandV2
from .v2 import Log as LogV2

from . import Signal as SignalV2


class Signal(Model):
    name: fields.Str()
    start: fields.Optional(fields.Int())  #
    length: fields.Optional(fields.Int())
    scale: fields.Optional(fields.Float(default=1.0))  #
    offset: fields.Optional(fields.Float(default=0.0))  #
    unit: fields.Optional(fields.Str())
    comment: fields.Optional(fields.Str())
    min_value: fields.Optional(fields.Float())
    max_value: fields.Optional(fields.Float())
    type: fields.Optional(fields.Str(default="unsigned"))  #
    byte_order: fields.Optional(fields.Str(default="little_endian"))  #
    mux: fields.Optional(fields.Str(default=""))  #
    mux_count: fields.Optional(fields.Int(default=1))  #

    def to_v2(self) -> SignalV2:
        def convert_type(type, length):
            if type == "unsigned":
                return "u" + str(length)
            elif type == "signed":
                return "i" + str(length)
            elif type == "float":
                return "f32"
            elif type == "double":
                return "f64"

        return SignalV2(
            name=self.name,
            start=self.start,
            length=self.length,
            scale=self.scale,
            offset=self.offset,
            unit=self.unit,
            comment=Comment(self.comment),
            min_value=self.min_value,
            max_value=self.max_value,
            type=convert_type(self.type, self.length),
            byte_order=self.byte_order,
            mux=self.mux,
            mux_count=self.mux_count,
        )


class Message(Model):
    name: fields.Str()
    id: fields.Int()
    dlc: fields.Int()
    signals: fields.Dict(fields.Str(), Signal)
    description: fields.Str()


class Log(Model):
    id: fields.Int()
    name: fields.Str()
    comment: fields.Str()
    string: fields.Str()
    n_args: fields.Optional(fields.Int())

    def to_v2(self) -> LogV2:
        return LogV2(self.id, self.name, self.string, comment=Comment(self.comment))


class Command(Model):
    name: fields.Str()
    n_args: fields.Optional(fields.Int())
    comment: fields.Str()
    id: fields.Int()
    args: fields.Dict(fields.Str(), Argument)
    rets: fields.Dict(fields.Str(), Argument)

    def to_v2(self, device) -> CommandV2:
        return CommandV2(
            name=self.name,
            id=self.id,
            args=list(self.args.values()),
            rets=list(self.rets.values()),
            comment=Comment(self.comment),
            n_args=self.n_args,
            device=device.name,
        )


class Config(Model):
    name: fields.Str()
    id: fields.Int()
    comment: fields.Str()
    type: fields.Str(default="unsigned")

    def to_v2(self, device) -> ConfigV2:
        # logging.info(device.name)
        return ConfigV2(
            name=self.name,
            id=self.id,
            comment=Comment(self.comment),
            type=self.type,
            device=device.name,
        )


class Device(Model):
    msgs: fields.Dict(fields.Str(), Message)
    cfgs: fields.Dict(fields.Str(), Config)
    cmds: fields.Dict(fields.Str(), Command)
    name: fields.Str()
    id: fields.Int()

    def to_v2(self) -> DeviceV2:
        return DeviceV2(
            name=self.name,
            id=self.id,
            commands=[cmd.to_v2(self) for cmd in self.cmds.values()],
            configs=[cfg.to_v2(self) for cfg in self.cfgs.values()],
        )


class FcpV1(Model):
    devices: fields.Dict(fields.Str(), Device)
    logs: fields.Dict(fields.Str(), Log)
    common: Device
    version: fields.Str()

    def get_messages(self, device=None):
        if device is not None:
            return self.devices[device].msgs.values()
        else:
            return [msg for dev in self.devices for msg in dev.msgs]

    def get_struct(self, device, message):
        if device == "common":
            message = self.common.msgs[message]
        else:
            message = self.devices[device].msgs[message]
        signals = sorted(message.signals.values(), key=lambda x: x.start)
        signals = [signal.to_v2() for signal in signals]
        return Struct(message.name, signals, comment=Comment(message.description))

    def convert_to_broadcast(self, device, message, struct):
        field = {
            "id": device.id + 32 * message.id,
            "dlc": message.dlc,
            "type": struct.name,
            "device": device.name if device.name != "common" else "all",
        }

        signals = sorted(message.signals.values(), key=lambda x: x.start)

        lengths = [signal.length for signal in signals]
        starts = [0] + list(accumulate(lengths))[:-1]

        defaults = {
            "mux": "",
            "mux_count": 1,
            "scale": 1.0,
            "offset": 0.0,
            "byte_order": "little_endian",
            "min_value": 0.0,
            "max_value": 0.0,
        }

        broadcast_signals = [
            self.convert_to_broadcast_signal(signal, defaults | {"start": starts[i]})
            for i, signal in enumerate(signals)
        ]
        broadcast_signals = list(filter(lambda x: x is not None, broadcast_signals))
        comment = Comment(message.description)
        return Broadcast(message.name, field, broadcast_signals, comment=comment)

    def convert_to_broadcast_signal(self, signal, defaults={}):
        signal = signal.to_dict()
        field = {
            name: signal[name]
            for name, value in defaults.items()
            if value != signal[name]
        }

        if len(field) == 0:
            return None
        else:
            return BroadcastSignal(signal["name"], field)

    def get_logs(self):
        return self.logs.values()

    def to_v2(self):
        structs = []
        broadcast = []

        for device in list(self.devices.values()) + [self.common]:
            logging.info(device.name)

            for message in device.msgs.values():
                struct = self.get_struct(device.name, message.name)
                structs.append(struct)
                broadcast.append(self.convert_to_broadcast(device, message, struct))

        return FcpV2(
            enums=[],
            structs=structs,
            devices=[device.to_v2() for device in self.devices.values()],
            broadcasts=broadcast,
            logs=[log.to_v2() for log in self.get_logs()],
            version="0.3",
        )


def fcp_v1_to_v2(fcp_v1: FcpV1):
    return fcp_v1.to_v2()
