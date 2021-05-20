import os
from copy import deepcopy
from pprint import pprint
from datetime import datetime
from typing import *

from .specs import Signal, Message, Device, Common, Spec, make_sid


def date():
    return str(datetime.now())


def decode_signature(device, message, signal):
    id = make_sid(device.id, message.id)
    return f"decode_{id}_{signal.name}"


def decode_signal_sig(device, message, signal):
    return f"{signal.type} {decode_signature(device, message, signal)} (CANdata msg);"


def msg_struct_sig(device, message):
    return f"msg_{device.name}_{message.name}_t"


def device_struct_sig(device):
    return f"dev_{device.name}_t"


def spec_struct_sig(spec):
    return "can_t"


def build_msg_sig(device):
    for message in device.msgs.values():
        message.type = msg_struct_sig(device, message)


def multiplexor(signal, message):
    if signal.mux == "" or signal.mux == None:
        signal.mux_str = ""
        return

    sig = message.get_signal(signal.mux)
    signal.mux_str = f"[{sig.max_value - sig.min_value + 1}]"


def dst_type_decide(signal: Signal):
    if signal.type == "float":
        return "float"

    if signal.type == "double":
        return "double"

    if signal.scale != 1:
        return "float"

    if signal.type == "signed":
        if signal.length <= 8:
            return "int8_t"
        elif signal.length <= 16:
            return "int16_t"
        elif signal.length <= 32:
            return "int32_t"
        elif signal.length <= 64:
            return "int64_t"

    if signal.length <= 8:
        return "uint8_t"
    elif signal.length <= 16:
        return "uint16_t"
    elif signal.length <= 32:
        return "uint32_t"
    elif signal.length <= 64:
        return "uint64_t"


def enum_endianess(signal):
    if signal.byte_order == "big_endian":
        return "BIG"
    else:
        return "LITTLE"


def enum_type(signal):
    return signal.type.upper()


def build_devices(spec, device, tpl):
    mux_counts = 0

    f_msgs: List[Message] = [msg for msg in device.msgs.values() if msg.frequency != 0]

    for message in device.msgs.values():
        message.multiplexor = ""
        message.mux_count = 0
        message.full_id = make_sid(device.id, message.id)
        for signal in message.signals.values():
            signal.dst_type = dst_type_decide(signal)
            signal.enum_endianess = enum_endianess(signal)
            signal.enum_type = enum_type(signal)
            multiplexor(signal, message)
            if signal.mux != "":
                message.multiplexor = signal.mux
            if signal.mux_count != 1:
                message.mux_count = signal.mux_count

    for f_msg in f_msgs:
        if f_msg.mux_count != 0:
            mux_counts += 1

    build_msg_sig(device)

    device.signature = device_struct_sig(device)

    h = tpl.render(
        "h.jinja", device=device, date=date(), mux_counts=mux_counts, f_msgs=f_msgs
    )
    c = tpl.render(
        "c.jinja",
        device=device,
        date=date(),
        f_msgs=f_msgs,
        mux_counts=mux_counts,
    )

    return [(device.name + "_can.h", h), (device.name + "_can.c", c)]


def build_can_ids(spec, tpl):
    for device in spec.devices.values():
        device.signature = device_struct_sig(device)

    spec.signature = spec_struct_sig(spec)

    build_msg_sig(spec.common)
    spec.common.signature = device_struct_sig(spec.common)

    logs = list(sorted(spec.logs.values(), key=lambda x: x.id))
    can_ids_h = tpl.render(
        "can_ids_h.jinja",
        devices=sorted(spec.devices.values(), key=lambda x: x.id),
        spec=spec,
        logs=logs,
        date=date(),
    )

    can_ids_c = tpl.render(
        "can_ids_c.jinja",
        devices=sorted(spec.devices.values(), key=lambda x: x.id),
        spec=spec,
        logs=logs,
        date=date(),
    )

    return [("can_ids.c", can_ids_c), ("can_ids.h", can_ids_h)]


def build_common(spec, tpl):
    mux_counts = 0
    for message in spec.common.msgs.values():
        sigs = message.signals
        for signal in message.signals.values():
            if signal.mux_count != 0:
                mux_counts += 1
            signal.dst_type = dst_type_decide(signal)
            signal.enum_endianess = enum_endianess(signal)
            signal.enum_type = enum_type(signal)
            multiplexor(signal, message)

    build_msg_sig(spec.common)
    spec.common.signature = device_struct_sig(spec.common)

    common_c = tpl.render(
        "common_c.jinja", spec=spec, date=date(), mux_counts=mux_counts
    )
    common_h = tpl.render(
        "common_h.jinja", spec=spec, date=date(), mux_counts=mux_counts
    )

    return [("common.c", common_c), ("common.h", common_h)]


def build_enums(spec, tpl):
    enums_h = tpl.render("enums_h.jinja", spec=spec, date=date())

    return [("can_enums.h", enums_h)]
