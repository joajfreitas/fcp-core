import json
from serde import Model, fields
from fcp.specs.broadcast import Broadcast, BroadcastSignal

from fcp.specs.struct import Struct
from .v2 import FcpV2
from . import Log, Argument, Comment
from .v2 import Device as DeviceV2
from .v2 import Config as ConfigV2
from .v2 import Command as CommandV2
from .v2 import Message as MessageV2
from . import Signal as SignalV2


class Signal(Model):
    """
    Signal node. Represents a CAN signal, similar to a DBC signal.

    :param name: Name of the Signal.
    :param start: Start bit
    :param length: Signal bit size.
    :param scale: Scaling applied to the signal's data.
    :param offset: Offset applied to the signal's data.
    :param unit: Unit of the Signal after applying scaling and offset.
    :param comment: Description of the Signal.
    :param min_value: Minimum value allowed to the Signal's data.
    :param max_value: Maximum value allowed to the Signal's data.
    :param type: Type of the Signal's data.
    :param mux: Name of the mux Signal. None if the Signal doesn't belong to a multiplexed Message.
    :param mux_count: Number of signals that the mux can reference for this Muxed signal.

    """

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
            type=self.type,
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

    def to_v2(self, device) -> MessageV2:
        return MessageV2(
            id=self.id * 32 + device.id,
            name=self.name,
            dlc=self.dlc,
            signals=list(self.signals.values()),
            description=self.description,
            device=device.name,
        )


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
            comment=self.comment,
            n_args=self.n_args,
            device=device.name,
        )


class Config(Model):
    name: fields.Str()
    id: fields.Int()
    comment: fields.Str()
    type: fields.Str(default="unsigned")

    def to_v2(self, device) -> ConfigV2:
        return ConfigV2(
            name=self.name,
            id=self.id,
            comment=self.comment,
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
        )


class FcpV1(Model):
    devices: fields.Dict(fields.Str(), Device)
    logs: fields.Dict(fields.Str(), Log)
    version: fields.Str()

    def get_messages(self, device=None):
        if device is not None:
            return self.devices[device].msgs.values()
        else:
            return [msg for dev in self.devices for msg in dev.msgs]

    def get_configs(self, device=None):
        if device is not None:
            return self.devices[device].cfgs.values()
        else:
            return [config for dev in self.devices for config in dev.cfgs]

    def get_commands(self, device=None):
        if device is not None:
            return self.devices[device].cmds.values()
        else:
            return [cmd for dev in self.devices for cmd in dev.cmds]

    # Poor function name since it is not a getter
    def get_struct(self, device, message):
        message = self.devices[device].msgs[message]
        signals = [signal.to_v2() for signal in message.signals.values()]
        return Struct(message.name, signals, comment=Comment(message.description))

    # Poor function name since it is not a getter
    def get_broadcast(self, device, message):
        signals = []
        message = self.devices[device].msgs[message]
        field = {"id": message.id, "dlc": message.dlc}
        signals += list(
            [self.get_broadcast_signal(signal) for signal in message.signals.values()]
        )
        comment = Comment(message.description)
        return Broadcast(message.name, field, signals, comment=comment)

    def get_broadcast_signal(self, signal):
        field = {
            "start": signal.start,
            "scale": signal.scale,
            "offset": signal.offset,
            "type": signal.type,
            "byte_order": signal.byte_order,
            "mux": signal.mux,
            "mux_count": signal.mux_count,
        }
        return BroadcastSignal(signal.name, field)

    def get_logs(self):
        return self.logs.values()

    def to_v2(self):
        structs = []
        broadcast = []

        for device in self.devices.values():
            for message in device.msgs.values():
                structs.append(self.get_struct(device.name, message.name))
                broadcast.append(self.get_broadcast(device.name, message.name))

        return FcpV2(
            devices=[device.to_v2() for device in self.devices.values()],
            structs=structs,
            broadcasts=broadcast,
            enums=[],
            version="0.3",
        )


def fcp_v1_to_v2(fcp_v1: FcpV1):
    return fcp_v1.to_v2()
