import json
import logging

from fcp.codegen import CodeGenerator
from fcp.verifier import BaseVerifier, simple_error
from fcp import v1


def broadcast_get_start(broadcast, name):
    signal = broadcast.get_signal(name)
    if signal is None:
        return None

    return signal.field.get("start")


def calculate_sizes(struct, broadcast):
    for signal in struct.signals:
        width = int(signal.type[1:])
        start = broadcast_get_start(broadcast, signal.name)
        yield start, width


def simple_message_allocation(sizes):
    acc = 0
    for start, length in sizes:
        if start is None:
            yield acc, length
        else:
            acc = start
            yield acc, length

        acc += length


def message_allocation(struct, broadcast):
    sizes = list(calculate_sizes(struct, broadcast))

    simple_allocation = list(simple_message_allocation(sizes))
    simple_allocation_success = True
    for start, length in simple_allocation:
        if start + length > 64:
            simple_allocation_success = False

    if simple_allocation_success:
        return simple_allocation
    else:
        return []


class Verifier(BaseVerifier):
    pass


def type_mapping(type):
    width = int(type[1:])
    type = type[0]

    if type == "u":
        return "unsigned"
    elif type == "i":
        return "signed"
    elif type == "f" and width == 32:
        return "float"
    elif type == "f" and width == 64:
        return "double"


def dst_type_mapping(type):
    width = int(type[1:])
    type = type[0]

    if type == "u" and width <= 8:
        return "uint8_t"
    elif type == "u" and width <= 16:
        return "uint16_t"
    elif type == "u" and width <= 32:
        return "uint32_t"
    elif type == "u" and width <= 64:
        return "uint64_t"
    elif type == "i" and width <= 8:
        return "int8_t"
    elif type == "i" and width <= 16:
        return "int16_t"
    elif type == "i" and width <= 32:
        return "int32_t"
    elif type == "i" and width <= 64:
        return "int64_t"
    elif type == "f" and width == 32:
        return "float"
    elif type == "f" and width == 64:
        return "double"


class Generator(CodeGenerator):
    def device_v1(self, device, broadcasts):
        return v1.Device(
            msgs={
                broadcast.name: self.message_v1(struct, broadcast, device.id)
                for struct, broadcast in broadcasts
            },
            cfgs={cfg.name: self.cfg_v1(cfg) for cfg in device.configs},
            cmds={cmd.name: self.cmd_v1(cmd) for cmd in device.commands},
            name=device.name,
            id=device.id,
        )

    def message_v1(self, broadcast, struct, device_id):
        broadcast_signals = {signal.name: signal for signal in broadcast.signals}
        broadcast_signals = [
            broadcast_signals.get(signal.name) for signal in struct.signals
        ]

        allocation = message_allocation(struct, broadcast)
        starts, lengths = zip(*allocation)

        return v1.Message(
            name=broadcast.name,
            id=(broadcast.field["id"] - device_id) >> 5,
            dlc=broadcast.field["dlc"],
            signals={
                signals[0].name: self.signal_v1(
                    signals[1], signals[0], starts[i], lengths[i]
                )
                for i, signals in enumerate(zip(struct.signals, broadcast_signals))
            },
            description=broadcast.comment.value,
        )

    def signal_v1(self, broadcast_signal, struct_signal, start, length):
        fields = {} if broadcast_signal is None else broadcast_signal.field
        return v1.Signal(
            name=struct_signal.name,
            mux_count=fields.get("mux_count") or 1,
            mux=fields.get("mux") or "",
            type=type_mapping(struct_signal.type),
            length=length,
            start=start,
            scale=fields.get("scale") or 1.0,
            offset=fields.get("offset") or 0.0,
            comment=struct_signal.comment.value,
            unit=struct_signal.unit or "",
        )

    def log_v1(self, log):
        return v1.Log(
            id=log.id,
            name=log.name,
            comment="" if log.comment is None else log.comment.value,
            string=log.string,
            n_args=log.n_args,
        )

    def cfg_v1(self, cfg):
        return v1.Config(
            name=cfg.name,
            id=cfg.id,
            comment="" if cfg.comment is None else cfg.comment.value,
            type=cfg.type,
        )

    def cmd_v1(self, cmd):
        return v1.Command(
            name=cmd.name,
            n_args=len(cmd.args),
            comment="" if cmd.comment is None else cmd.comment.value,
            id=cmd.id,
            args={},
            rets={},
        )

    def generate(self, fcp, output_path, templates={}, skels={}):
        structs = {struct.name: struct for struct in fcp.structs}

        broadcasts = {}
        for broadcast in fcp.broadcasts:
            device = broadcast.field["device"]
            type = broadcast.field["type"]
            if device not in broadcasts.keys():
                broadcasts[device] = []

            broadcasts[device].append((broadcast, structs[type]))

        fcp_v1 = v1.FcpV1(
            devices={
                device.name: self.device_v1(device, broadcasts[device.name])
                for device in fcp.devices
            },
            logs={log.name: self.log_v1(log) for log in fcp.logs},
            common=v1.Device(
                msgs={
                    broadcast.name: self.message_v1(struct, broadcast, 0)
                    for struct, broadcast in broadcasts["all"]
                },
                cfgs={},
                cmds={},
                name="common",
                id=0,
            ),
            version="2",
        )
        return {output_path: fcp_v1.to_json(indent=4)}
