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

from .spec import *


def check_device(device):
    if len(device.msgs.keys()) == 0:
        return False, f"{device.name}: Device without messages"
    if device.id > 31:
        return False, f"{device.name}: dev_id bigger than 32"

    if len(device.name.strip()) != len(device.name):
        return False, f"{device.name}: Device name contains whitespace"

    return True, ""


def check_message(message):
    if len(message.signals.keys()) == 0:
        return False, f"{message.name}: Message without signals"

    if len(message.name.strip()) != len(message.name):
        return False, f"{message.name}: Message name contains whitespace"

    return True, ""


def check_device_message(message):
    r, msg = check_message(message)
    if not r:
        return r, msg

    if message.id > 63:
        return False, f"{message.name}: msg_id bigger than 64"
    # elif message.id < 32:
    #    return False, f"{message.name}: device has message id smaller than 32"

    return True, ""


def check_signal(key, signal):
    if signal.length > 64:
        return False, f"{signal.name}: signal length is bigger than 64"
    elif signal.length + signal.start > 64:
        return False, f"{signal.name}: signal outside 64 bit range"
    elif signal.start < 0:
        return False, f"{signal.name}: signals starts before bit 0"
    elif signal.length == 0:
        return False, f"{signal.name}: 0 length signal"
    elif not (
        signal.type == "unsigned"
        or signal.type == "signed"
        or signal.type == "double"
        or signal.type == "float"
    ):
        return (
            False,
            f("{signal.name}: Unsuported signal type, should be {unsigned, signed, double, float}",)
        )
    elif signal.type == "float" and signal.length != 32:
        return False, f"{signal.name}: float signal length is different than 32"
    elif signal.type == "double" and signal.length != 64:
        return False, f"{signal.name}: double signal length is different than 64"
    elif not (
        signal.byte_order == "little_endian" or signal.byte_order == "big_endian"
    ):
        return False, f"{signal.name}: signal endianess not suported"
    elif signal.name[0].isdigit():
        return False, f"{signal.name}: signal name starts with a number"
    elif signal.scale == 1 and signal.offset != 0:
        return (
            False,
            f"{signal.name}: signal offset is different than 0 for a scale of 1",
        )
    elif signal.scale != 1 and signal.length > 32:
        return (
            False,
            f"{signal.name}: scaling for variables bigger than 32 bit is unsuported",
        )
    elif key != signal.name:
        return False, f"{signal.name}: signal key is not equal to signal name"

    if len(signal.name.strip()) != len(signal.name):
        return False, f"{signal.name}: Device name contains whitespace"

    return True, ""


def check_common(message):
    r = check_message(message)
    if not r:
        return r

    if message.id > 63:
        return False, f"{message.name}: msg_id bigger than 64"
    elif message.id >= 32:
        return False, f"{message.name}: common has message id bigger or equal to 32"

    return True, ""


def check_log(log):
    if log.id < 0:
        return False, f"{log.name}: log id is smaller than 0"
    if log.id > 255:
        return False, f"{log.name} log id is bigger than 255"
    try:
        int(log.id)
    except Exception as e:
        return False, f"{log.name} is not a valid integer"

    return True, ""


def check_logs(logs):
    log_ids = []

    for log in logs.values():
        r, m = check_log(log)
        if r == False:
            return r, m

    for log in logs.values():
        if log.id in log_ids:
            return False, f"{log.name}: found duplicate log id"
        log_ids.append(log.id)

    return True, ""


def validate(logger, j, spec=None):
    if spec == None:
        spec = Spec()
        spec.decompile(j)

    r, msg = check_logs(spec.logs)
    if r == False:
        return r, msg

    for message in spec.common.msgs.values():
        r, msg = check_common(message)
        if not r:
            return r, msg

    device_ids = []
    device_names = []
    message_names = []
    signal_names = []
    for device in spec.devices.values():
        if device.id in device_ids:
            return False, f"{device.name}: duplicate device id"
        device_ids.append(device.id)

        if device.name in device_names:
            return False, f"{device.name}: duplicate device name"
        device_names.append(device.name)

        r, msg = check_device(device)
        if not r:
            return r, msg

        message_ids = []
        for message in device.msgs.values():
            if message.id in message_ids:
                return False, f"{device.name}: {message.name} duplicate message id"
            message_ids.append(message.id)

            if message.name in message_names:
                return False, f"{device.name}: {message.name} duplicate message name"
            message_names.append(message.name)

            if type(message) != Message:
                continue
            r, msg = check_device_message(message)
            if not r:
                return r, msg

            for key, signal in message.signals.items():
                if signal.name in signal_names:
                    return False, f"{message.name}: {signal.name} duplicate signal name"

                signal_names.append(signal.name)
                r, msg = check_signal(key, signal)
                if not r:
                    return r, msg

    return True, ""
