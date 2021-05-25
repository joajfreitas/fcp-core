"""c-generator.

Usage:
  validator.py validate <json>
  validator.py (-h | --help)
  validator.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import json
import logging

import colorful as cf

from .specs import *


check_table = {
    "sig": {},
    "msg": {},
    "dev": {},
    "spec": {},
    "cmd": {},
    "cfg": {},
    "log": {},
}


def check_decorator(category):
    def closure(f):
        if category not in check_table.keys():
            print(f"{category} category not available")
            return
        check_table[category][f.__name__] = f

    return closure


def fail_msg(node, msg, level="error"):
    def location(node):
        if node.parent is None:
            return node.name

        return location(node.parent) + "/" + node.name

    return (level, f"{location(node)}: {msg}")


@check_decorator("sig")
def signal_length(signal):
    if signal.length > 64 or signal.length <= 0:
        return fail_msg(signal, f"signal length is {signal.length}")


@check_decorator("sig")
def signal_start(signal):
    if signal.start > 63 or signal.start < 0:
        return fail_msg(signal, f"signal start is {signal.start}")


@check_decorator("sig")
def signal_total_length(signal):
    if signal.start + signal.length > 64:
        level = "error"
        if signal.byte_order == "big_endian":
            level = "warning"
        else:
            level = "error"

        return fail_msg(signal, f"signal end is bigger than 64", level)


@check_decorator("sig")
def signal_type(signal):
    types = ["unsigned", "signed", "double", "float"]
    if signal.type not in types:
        return fail_msg(
            signal, f"signal type is {signal.type}. Valid types are: {types}"
        )
    if signal.type == "float" and signal.length != 32:
        return fail_msg(signal, f"signal is float but length is {signal.length} != 32")

    if signal.type == "double" and signal.length != 64:
        return fail_msg(signal, f"signal is double but length is {signal.length} != 64")


@check_decorator("sig")
def signal_endianess(signal):
    endianess = ["little_endian", "big_endian"]

    if signal.byte_order not in endianess:
        return fail_msg(
            signal, f"signal endianess not supported. Valid values are: {endianess} got {signal.byte_order}"
        )


@check_decorator("sig")
def signal_name(signal):
    if not signal.name.isidentifier():
        return fail_msg(signal, f"{signal.name} is not a valid identifier")


@check_decorator("sig")
def signal_scaling(signal):
    if signal.scale == 1 and signal.offset != 0:
        return fail_msg(
            signal,
            f"{signal.name}: signal offset is different than 0 for a scaling of 1",
        )

    if signal.scale != 1 and signal.length > 32:
        return fail_msg(
            signal, f"scaling is not supported for variables bigger than 32 bits"
        )


@check_decorator("sig")
def signal_mux(signal):
    if signal.mux == 0:
        return fail_msg(signal, f"Mux count is 0, should be >= 1")


@check_decorator("sig")
def signal_mux_count(sig):
    if int(sig.mux_count) == 0:
        return fail_msg(sig, f"Mux count *cannot* be 0")


@check_decorator("msg")
def msg_mux(msg):
    muxeds = [signal.mux for signal in msg.signals.values() if signal.mux != ""]
    if len(muxeds) == 0:
        return

    mux = msg.signals.get(muxeds[0])
    if mux == None:
        return fail_msg(msg, f"Cannot find mux signal in multiplexed message got {muxeds[0]}")

    if 2 ** mux.length < mux.mux_count:
        return fail_msg(msg, f"Mux cannot fit all possible multiplexed values")


@check_decorator("msg")
def msg_name(msg):
    if not msg.name.isidentifier():
        return fail_msg(msg, f"Message name is not a valid identifier")


@check_decorator("msg")
def msg_id(msg):
    if msg.id > 64 or msg.id < 0:
        return fail_msg(msg, f"Message id is not valid: {msg.id}")


@check_decorator("msg")
def msg_dlc(msg):
    if msg.dlc > 8 or msg.dlc < 0:
        return fail_msg(msg, f"Message dlc is not valid: {msg.dlc}")


@check_decorator("msg")
def msg_frequency(msg):
    if msg.frequency < 0:
        return fail_msg(msg, f"Message frequency is not valid: {msg.frequency}")


@check_decorator("msg")
def msg_overlapping_signals(msg):
    values = []
    for signal in msg.signals.values():
        values += list(range(signal.start, signal.start + signal.length))

    s = set(values)

    if len(s) != len(values):
        return fail_msg(msg, f"Message has overlapping signals")


@check_decorator("dev")
def dev_name(dev):
    if not dev.name.isidentifier():
        return fail_msg(dev, f"Device name is not a valid identifier")


@check_decorator("dev")
def dev_id(dev):
    if dev.id > 31 or dev.id < 0:
        return fail_msg(dev, f"Device id is not valid: {dev.id}")


@check_decorator("dev")
def dev_overlapping_msg_ids(dev):
    ids = [msg.id for msg in dev.msgs.values()]
    ids_set = set(ids)

    if len(ids_set) != len(ids):
        return fail_msg(dev, f"Device has overlapping msg ids")


@check_decorator("log")
def log_id(log):
    if log.id > 255 and log.id < 0:
        return fail_msg(log, f"Log id is not valid: {log.id}")


@check_decorator("log")
def log_n_args(log):
    if log.n_args > 3 or log.n_args < 0:
        return fail_msg(log, f"Log n args is not valid: {log.n_args}")


@check_decorator("log")
def log_name(log):
    if not log.name.isidentifier():
        return fail_msg(log, f"Log name is not valid: {log.name}")


@check_decorator("cfg")
def cfg_name(cfg):
    if not cfg.name.isidentifier():
        return fail_msg(cfg, f"Cfg name is not valid: {cfg.name}")


@check_decorator("cfg")
def cfg_id(cfg):
    if cfg.id > 255 and cfg.id < 0:
        return fail_msg(cfg, f"Cfg id is not valid: {cfg.id}")


@check_decorator("cmd")
def cmd_name(cmd):
    if not cmd.name.isidentifier():
        return fail_msg(cmd, f"Cmd name is not valid: {cmd.name}")


@check_decorator("cmd")
def cmd_id(cmd):
    if cmd.id > 255 and cmd.id < 0:
        return fail_msg(cmd, f"Cmd id is not valid: {cmd.id}")


@check_decorator("cmd")
def cmd_n_args(cmd):
    if cmd.n_args > 3 and cmd.n_args < 0:
        return fail_msg(cmd, f"Cmd n args is not valid: {cmd.n_args}")


@check_decorator("spec")
def spec_overlapping_dev_ids(spec):
    ids = [dev.id for dev in spec.devices.values()]
    ids_set = set(ids)

    if len(ids_set) != len(ids):
        return fail_msg(spec, f"There are overlapping device ids")


@check_decorator("dev")
def spec_same_name_configs(device):
    cfgs = []
    for cfg in device.cfgs.values():
        cfgs += [cfg.name]

    cfgs_set = set()

    for cfg in cfgs:
        if cfgs.count(cfg) > 1:
            cfgs_set.add(cfg)

    if len(cfgs_set) != 0:
        return fail_msg(
            spec,
            "There are overlapping config names [{}]".format(", ".join(cfgs_set)),
            level="warning",
        )


@check_decorator("dev")
def spec_same_name_commands(dev):
    cmds = []
    for cmd in dev.cmds.values():
        cmds += [cmd.name]

    cmds_set = set()

    for cmd in cmds:
        if cmds.count(cmd) > 1:
            cmds_set.add(cmd)

    if len(cmds_set) != 0:
        return fail_msg(
            spec,
            "There are overlapping command names [{}]".format(", ".join(cmds_set)),
            level="warning",
        )


def spec_repeated_names(spec):
    def get_signal_names(spec):
        for dev in spec.devices.values():
            for msg in dev.msgs.values():
                for signal in msg.signals.values():
                    yield signal.name

    names = get_signal_names(spec)

    if len(set(names)) != len(names):
        return fail_msg(spec, f"There are repeated signal names")


def check(category, arg):
    failed = []

    if category not in check_table.keys():
        print(f"{category} category not available")
        return failed

    for check in check_table[category].values():
        r = check(arg)

        if r:
            failed.append(r)

    return failed


def validate(spec):
    failed = []
    failed += check("spec", spec)

    for log in spec.logs.values():
        failed += check("log", log)
    for message in spec.common.msgs.values():
        failed += check("msg", message)
    for device in spec.devices.values():
        failed += check("dev", device)
        for message in device.msgs.values():
            failed += check("msg", message)
            for signal in message.signals.values():
                failed += check("sig", signal)

        for cfg in device.cfgs.values():
            failed += check("cfg", cfg)

        for cmd in device.cmds.values():
            failed += check("cmd", cmd)

    return failed


def format_error(level, message):
    if level == "warning":
        level = cf.yellow(level)
    elif level == "error":
        level = cf.red(level)
    else:
        level = cf.blue(level)

    return f"{level}: {message}"
