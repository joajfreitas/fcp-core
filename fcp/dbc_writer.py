from cantools.database.can.database import Database as CanDatabase
from cantools.database.can.message import Message as CanMessage
from cantools.database.can.signal import Signal as CanSignal
from cantools.database.can.node import Node as CanNode

from cantools.database import *

from .specs import *

import copy


def is_float(signal):
    return signal.type == "float" or signal.type == "double"


def is_signed(signal):
    return signal.type == "signed"


def is_decimal(signal):
    return signal.type == "signed" or signal.type == "unsigned"


def is_multiplexer(signal, mux_signals):
    return signal.name in mux_signals


# multiplexer_signal=None,


def make_signal(signal, mux_signals, dev_name):
    def make_signal_closure(name, signal, mux_signals, ids):
        return CanSignal(
            name,
            signal.start + (7 if signal.byte_order == "big_endian" else 0),
            signal.length,
            byte_order=signal.byte_order,
            scale=float(signal.scale),
            offset=float(signal.offset),
            minimum=int(signal.min_value),
            maximum=int(signal.max_value),
            unit=signal.unit,
            comment=signal.comment,
            is_float=is_float(signal),
            is_signed=is_signed(signal),
            decimal=is_decimal(signal),
            is_multiplexer=is_multiplexer(signal, mux_signals),
            multiplexer_ids=ids,
            multiplexer_signal=[signal.mux],
            receivers=[dev_name],
        )

    if signal.mux_count == 1:
        #if len(mux_signals) > 0:
        #    yield make_signal_closure(signal.name, signal, mux_signals, [1])
        #else:
        yield make_signal_closure(signal.name, signal, mux_signals, None)

        return

    for i in range(signal.mux_count):
        yield make_signal_closure(signal.name + str(i), signal, mux_signals, [i])


def process_mux_signals(signals):
    mux_signals = []
    for key, val in signals.items():
        if val.mux not in mux_signals:
            mux_signals.append(val.mux)

    return mux_signals


def write_dbc(spec, dbc):

    messages = []
    nodes = []

    for dev_name, dev in spec.devices.items():
        nodes.append(CanNode(dev.name, ""))
        for msg_name, msg in dev.msgs.items():
            id = make_sid(dev.id, msg.id)

            mux_signals = process_mux_signals(msg.signals)
            signals = []
            for sig_name, sig in msg.signals.items():
                for sig in make_signal(sig, mux_signals, dev_name):
                    signals.append(sig)

            messages.append(
                CanMessage(id, msg.name, msg.dlc, signals, senders=[dev_name])
            )

    db = CanDatabase(messages=messages, nodes=nodes)
    dump_file(db, dbc)
