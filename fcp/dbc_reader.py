"""dbc-reader.

Usage:
  dbc-reader read <dbc> <json> [<device-config>]
  dbc-reader (-h | --help)
  dbc-reader --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import logging
import json
import cantools

from .spec import (
    Spec,
    Device,
    Message,
    Signal,
    Log,
    Command,
    Argument,
    Config,
    make_sid,
    decompose_id,
)

from pprint import pprint


def find_type(signal):
    if signal.is_float:
        return "float"
    elif signal.is_signed:
        return "signed"
    else:
        return "unsigned"


def query_user_ids(dev_id):
    if dev_id not in query_user_ids.ids.keys():
        print(dev_id)
        query_user_ids.ids[dev_id] = input("Device name: ")
        return query_user_ids.ids[dev_id]
    else:
        return query_user_ids.ids[dev_id]


query_user_ids.ids = {}


def default_device(device):
    version = Config("version", 0, "git version")
    device.add_cfg(version)


def default_common_log_msg(spec):
    log_msg = Message(name="log", id=0)
    level = Signal(name="level", start=0, length=3)
    n_args = Signal(start=3, length=2, name="n_args")
    err_code = Signal(start=8, length=8, name="err_code")
    arg1 = Signal(start=16, length=16, name="arg1")
    arg2 = Signal(start=32, length=16, name="arg2")
    arg3 = Signal(start=48, length=16, name="arg3")
    log_msg.add_signal(level)
    log_msg.add_signal(n_args)
    log_msg.add_signal(err_code)
    log_msg.add_signal(arg1)
    log_msg.add_signal(arg2)
    log_msg.add_signal(arg3)

    spec.common.add_msg(log_msg)


def default_common_cfg_msg(spec):
    req_get = Message(name="req_get", id=3)
    dst = Signal(name="dst", start=0, length=5)
    id = Signal(name="id", start=8, length=8)

    req_get.add_signal(id)
    req_get.add_signal(dst)
    spec.common.add_msg(req_get)

    ans_get = Message(name="ans_get", id=4)
    id = Signal(name="id", start=0, length=5)
    dst = Signal(name="dst", start=8, length=8)
    data = Signal(name="data", start=16, length=32)

    ans_get.add_signal(id)
    ans_get.add_signal(dst)
    ans_get.add_signal(data)
    spec.common.add_msg(ans_get)

    req_set = Message(name="req_set", id=5)
    dst = Signal(name="dst", start=0, length=5)
    id = Signal(name="id", start=8, length=8)
    data = Signal(name="data", start=16, length=32)

    req_set.add_signal(id)
    req_set.add_signal(dst)
    req_set.add_signal(data)
    spec.common.add_msg(req_set)

    ans_set = Message(name="ans_set", id=6)
    id = Signal(name="id", start=0, length=5)
    dst = Signal(name="dst", start=8, length=8)
    data = Signal(name="data", start=16, length=32)

    ans_set.add_signal(id)
    ans_set.add_signal(dst)
    ans_set.add_signal(data)
    spec.common.add_msg(ans_set)


def default_common_cmd_msg(spec):
    cmd_args_msg = Message(name="send_cmd", id=1)
    dst = Signal(name="dst", start=0, length=5)
    id = Signal(name="id", start=8, length=8)
    arg1 = Signal(start=16, length=16, name="arg1")
    arg2 = Signal(start=32, length=16, name="arg2")
    arg3 = Signal(start=48, length=16, name="arg3")

    cmd_args_msg.add_signal(dst)
    cmd_args_msg.add_signal(id)
    cmd_args_msg.add_signal(arg1)
    cmd_args_msg.add_signal(arg2)
    cmd_args_msg.add_signal(arg3)

    spec.common.add_msg(cmd_args_msg)

    cmd_return = Message(name="return_cmd", id=2)
    id = Signal(name="id", start=8, length=8)
    ret1 = Signal(start=16, length=16, name="ret1")
    ret2 = Signal(start=32, length=16, name="ret2")
    ret3 = Signal(start=48, length=16, name="ret3")

    cmd_return.add_signal(id)
    cmd_return.add_signal(ret1)
    cmd_return.add_signal(ret2)
    cmd_return.add_signal(ret3)

    spec.common.add_msg(cmd_return)


def default_common(spec):
    default_common_log_msg(spec)
    default_common_cfg_msg(spec)
    default_common_cmd_msg(spec)


def default_spec_logs(spec):
    log_error = Log(
        id=0, name="wrong_log_id", n_args=0, string="Log code was not found"
    )
    spec.add_log(log_error)

    cfg_error = Log(
        id=1, name="wrong_cfg_id", n_args=0, string="Cfg code was not found"
    )

    spec.add_log(cfg_error)


def default_spec(spec):
    default_spec_logs(spec)


def default_configs(spec):
    default_common(spec)

    default_spec(spec)
    for device in spec.devices.values():
        default_device(device)


def read_dbc(dbc, json_file, device_config, logger):
    # if device name configuration is provided load it
    if device_config:
        with open(device_config) as f:
            dev_config = json.loads(f.read())

    db = cantools.database.load_file(dbc)

    spec = Spec()

    for message in db.messages:
        logger.debug("db message " + str(message))
        sid = message.frame_id
        dev_id, msg_id = decompose_id(sid)

        # no device id configuration provided, dynamically ask for it
        if not device_config:
            device_name = query_user_ids(dev_id)
        else:
            device_name = dev_config[str(dev_id)]

        device = Device(id=dev_id, name=device_name, msgs={})

        msg = Message(name=message.name, id=msg_id, dlc=message.length, signals={})

        err = spec.add_device(device)
        logger.debug("add device " + str(dev_id) + " " + str(err) + " " + str(device))
        err = spec.devices[device.name].add_msg(msg)
        logger.debug("add message " + str(msg_id) + " " + str(err) + " " + str(msg))

        for signal in message.signals:
            t = find_type(signal)
            print(
                signal.multiplexer_signal, signal.is_multiplexer, signal.multiplexer_ids
            )
            sig = Signal(
                name=signal.name,
                start=signal.start,
                length=signal.length,
                scale=signal.scale or 1,
                offset=signal.offset or 0,
                unit=signal.unit or "",
                comment=signal.comment or "",
                min_value=signal.minimum or 0,
                max_value=signal.maximum or 0,
                byte_order=signal.byte_order or "little_endian",
                type=t or "unsigned",
                mux=signal.multiplexer_signal or "",
                mux_count=1,
            )
            err = spec.devices[device.name].get_msg(message.name).add_signal(sig)

            logger.debug(
                "add signal " + str(sig.name) + " " + str(err) + " " + str(sig)
            )

    default_configs(spec)
    j = spec.compile()
    # pprint(j)
    j["version"] = "0.2"

    with open(json_file, "w") as f:
        f.write(json.dumps(j, sort_keys=True, indent=4))


def init(json_file, logger):
    spec = Spec()
    default_configs(spec)
    logger.info("added default configs ✅")
    j = spec.compile()

    with open(json_file, "w") as f:
        f.write(json.dumps(j, sort_keys=True, indent=4))
