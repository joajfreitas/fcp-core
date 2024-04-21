import logging
import itertools
import operator
import datetime
from collections import Counter

from jinja2 import Template

from fcp.result import Ok, Error
from fcp.codegen import CodeGenerator
from fcp.verifier import BaseVerifier, simple_error
import fcp.specs.v2


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
        return Ok(simple_allocation)

    return Error(
        f"Message allocation failed for broadcast {broadcast.name}. {simple_allocation}"
    )


class Verifier(BaseVerifier):
    @simple_error
    def check_struct_size(self, struct):
        total_msg_size = sum([int(signal.type[1:]) for signal in struct.signals])
        return (
            total_msg_size > 64,
            f"Struct {struct.name} is too big. Current size is {total_msg_size} bits, maximum is 64.",
        )

    @simple_error
    def check_broadcast_field_id(self, broadcast):
        return (
            "id" not in broadcast.field.keys(),
            f"Broadcast {broadcast.name} has no field id",
        )

    @simple_error
    def check_broadcast_field_dlc(self, broadcast):
        return (
            "dlc" not in broadcast.field.keys(),
            f"Broadcast {broadcast.name} has no field dlc",
        )

    @simple_error
    def check_broadcast_field_device(self, broadcast):
        return (
            "device" not in broadcast.field.keys(),
            f"Broadcast {broadcast.name} has no field device",
        )

    @simple_error
    def check_broadcast_field_type(self, broadcast):
        return (
            "type" not in broadcast.field.keys(),
            f"Broadcast {broadcast.name} has no field type",
        )

    @simple_error
    def check_broadcast_signal__start_in_range(self, signal):
        start = signal.field.get("start") or 0
        return (
            start >= 64,
            f"Broadcast signal {signal.name} start is out of range ({start})",
        )

    @simple_error
    def check_broadcast_id(self, broadcast):
        id = broadcast.field.get("id") or 0
        return (
            id >= 2**11,
            f"Broadcast {broadcast.name} id is too big. Current id is {id}, maximum is {2**11 - 1}.",
        )

    def check_paired_struct_mux_count(self, struct, broadcast):
        mux_count = broadcast.get_mux_count()
        mux = broadcast.get_mux()
        if mux is None:
            return Ok(())

        signal = struct.get_signal(mux)
        width = int(signal.type[1:])
        if 2**width < mux_count:
            return Error(
                self.error_logger.log_node(
                    signal,
                    f"Broadcast {broadcast.name} mux {mux} (size = {width} bits) cannot represent all mux variations: {mux_count}",
                )
            )
        else:
            return Ok(())

    def check_paired_struct_overlapping_signals(self, struct, broadcast):
        # bits = [0] * 64
        overlapping = {}
        for i in range(64):
            overlapping[i] = []

        allocations = message_allocation(struct, broadcast).unwrap()

        for i, allocation in enumerate(allocations):
            start, length = allocation
            for j in range(start, start + length):
                overlapping[j].append(struct.signals[i].name)

        overlapping = list(
            filter(lambda x: len(x) >= 2, set(map(tuple, overlapping.values())))
        )

        if len(overlapping) == 0:
            return Ok(())

        return Error(
            self.error_logger.log_node(
                broadcast,
                f"Overlapping signals in broadcast {broadcast.name}: \n\t* "
                + "\n\t* ".join(map(str, overlapping))
                + "\n",
            )
        )

    @simple_error
    def check_paired_signal_in_range(self, struct_signal, broadcast_signal):
        width = int(struct_signal.type[1:])
        start = broadcast_signal.field.get("start") or 0

        return (
            start + width - 1 >= 64,
            f"Signal {struct_signal.name} has length {width} and starts in bit {start} which makes it out of range for a 64 bit CAN message",
        )


class Generator(CodeGenerator):
    def __init__(self):
        pass

    def type_mapping(self, type):
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

    def dst_type_mapping(self, type):
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

    def create_msg(self, broadcast, device, types):
        dev_id = device.id
        sid = int(broadcast.field["id"])
        msg_id = int((sid - dev_id) / 32)

        struct = types[broadcast.field["type"]]

        allocation = message_allocation(struct, broadcast).unwrap()
        starts, lengths = zip(*allocation)

        broadcast_signals = {signal.name: signal.field for signal in broadcast.signals}
        broadcast_signals = [
            broadcast_signals.get(signal.name) or {} for signal in struct.signals
        ]

        separator = (
            "\n" if broadcast.comment.value != "" and struct.comment.value != "" else ""
        )
        comment = struct.comment.value + separator + broadcast.comment.value

        msg = {
            "name": broadcast.name,
            "id": msg_id,
            "dlc": broadcast.field["dlc"],
            "type": f"{broadcast.name}_t",
            "mux_count": 0,
            "comment": comment,
            "signals": {
                signal.name: {
                    "mux_count": broadcast_signals[i].get("mux_count") or 0,
                    "mux": broadcast_signals[i].get("mux") or "",
                    "name": signal.name,
                    "type": self.type_mapping(signal.type),
                    "dst_type": self.dst_type_mapping(signal.type),
                    "length": lengths[i],
                    "start": starts[i],
                    "scale": broadcast_signals[i].get("scale") or 1.0,
                    "offset": broadcast_signals[i].get("offset") or 0.0,
                    "comment": signal.comment.value,
                    "unit": signal.unit or "",
                }
                for i, signal in enumerate(struct.signals)
            },
        }

        return msg

    def config(self, fcp):

        types = {struct.name: struct for struct in fcp.structs}
        types.update({enum.name: enum for enum in fcp.enums})

        devices = {}

        for device in fcp.devices:
            devices[device.name] = {
                "name": device.name,
                "signature": f"dev_{device.name}_t",
                "id": int(device.id),
                "msgs": {},
                "cfgs": {},
                "cmds": {},
            }

            for cmd in device.commands:
                devices[device.name]["cmds"][cmd.name] = {
                    "name": cmd.name,
                    "id": cmd.id,
                }

            for cfg in device.configs:
                devices[device.name]["cfgs"][cfg.name] = {
                    "name": cfg.name,
                    "id": cfg.id,
                }

            for broadcast in fcp.broadcasts:
                if broadcast.field["device"] == device.name:
                    devices[device.name]["msgs"][broadcast.name] = self.create_msg(
                        broadcast, device, types
                    )

        common_dev = v2.device.Device(name="common", id=0, commands=[], configs=[])
        common = {"signature": "dev_common_t", "name": "common", "msgs": {}}
        for broadcast in fcp.broadcasts:
            if broadcast.field["device"] == "all":
                common["msgs"][broadcast.name] = self.create_msg(
                    broadcast, common_dev, types
                )

        logging.info(common)

        return {
            "signature": "can_t",
            "devices": devices,
            "common": common,
            "enums": fcp.enums,
            "logs": fcp.logs,
        }

    def generate_can_ids_h(self, template, spec):
        return template.render(
            date=datetime.datetime.now(),
            spec=spec,
        )

    def generate_can_ids_c(self, template, spec):
        return template.render(date=datetime.datetime.now(), spec=spec)

    def generate_common_c(self, template, spec):
        return template.render(date=datetime.datetime.now(), spec=spec)

    def generate_common_h(self, template, spec):
        return template.render(
            date=datetime.datetime.now(),
            spec=spec,
        )

    def generate_c(self, template, device):
        return template.render(
            date=datetime.datetime.now(),
            device=device,
        )

    def generate_h(self, template, device):
        return template.render(
            date=datetime.datetime.now(),
            device=device,
        )

    def generate(self, fcp, templates={}, skels={}):
        templates = {name: Template(template) for name, template in templates.items()}
        spec = self.config(fcp)

        fileset = {
            "can_ids.h": self.generate_can_ids_h(templates.get("can_ids_h"), spec),
            "can_ids.c": self.generate_can_ids_c(templates.get("can_ids_c"), spec),
            "common.c": self.generate_common_c(templates.get("common_c"), spec),
            "common.h": self.generate_common_h(templates.get("common_h"), spec),
            "candata.h": skels["candata.h"],
            "signal_parser.c": skels["signal_parser.c"],
            "signal_parser.h": skels["signal_parser.h"],
            "can_cfg.c": skels["can_cfg.c"],
            "can_cfg.h": skels["can_cfg.h"],
            "can_cmd.c": skels["can_cmd.c"],
            "can_cmd.h": skels["can_cmd.h"],
            "can_log.c": skels["can_log.c"],
            "can_log.h": skels["can_log.h"],
            "main.c": skels["main.c"],
        }

        for dev in fcp.devices:
            device = spec["devices"][dev.name]
            fileset[f"{dev.name}_can.c"] = self.generate_c(templates.get("c"), device)
            fileset[f"{dev.name}_can.h"] = self.generate_h(templates.get("h"), device)

        return fileset
