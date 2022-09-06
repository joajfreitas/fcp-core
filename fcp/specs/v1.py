import json
from serde import Model, fields

from .v2 import FcpV2
from . import Signal, Log, Argument
from .v2 import Device as DeviceV2
from .v2 import Config as ConfigV2
from .v2 import Command as CommandV2
from .v2 import Message as MessageV2


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

    def get_logs(self):
        return self.logs.values()

    def to_v2(self):
        msgs = []
        cmds = []
        cfgs = []

        for device in self.devices.values():
            msgs += list([x.to_v2(device) for x in self.get_messages(device.name)])
            cmds += list([x.to_v2(device) for x in self.get_commands(device.name)])
            cfgs += list([x.to_v2(device) for x in self.get_configs(device.name)])

        return FcpV2(
            devices=[device.to_v2() for device in self.devices.values()],
            messages=msgs,
            configs=cfgs,
            commands=cmds,
            logs=[log for log in self.get_logs()],
            enums=[],
            version="0.3",
        )


def fcp_v1_to_v2(fcp_v1: FcpV1):
    return fcp_v1.to_v2()
