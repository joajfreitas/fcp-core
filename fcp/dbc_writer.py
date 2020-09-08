from cantools.database.can.database import Database as CanDatabase
from cantools.database.can.message import Message as CanMessage
from cantools.database.can.signal import Signal as CanSignal
from cantools.database.can.node import Node as CanNode

from cantools.database import *

from .spec import *


def is_float(signal):
    return signal.type == "float" or signal.type == "double"


def is_signed(signal):
    return signal.type == "signed"


def is_decimal(signal):
    return signal.type == "signed" or signal.type == "unsigned"


def is_multiplexer(signal, mux_signals):
    return signal.name in mux_signals


# multiplexer_signal=None,


def make_signal(signal, mux_signals):
    def make_signal_closure(signal, mux_signals, ids):
        return CanSignal(
            signal.name,
            signal.start,
            signal.length,
            byte_order=signal.byte_order,
            scale=signal.scale,
            offset=signal.offset,
            minimum=signal.min_value,
            maximum=signal.max_value,
            unit=signal.unit,
            comment=signal.comment,
            is_float=is_float(signal),
            is_signed=is_signed(signal),
            decimal=is_decimal(signal),
            is_multiplexer=is_multiplexer(signal, mux_signals),
            multiplexer_ids=ids,
            multiplexer_signal=[signal.mux],
        )

    if signal.mux_count == 1:
        yield make_signal_closure(signal, mux_signals, None)
        return

    for i in range(signal.mux_count):
        yield make_signal_closure(signal, mux_signals, [i])


def process_mux_signals(signals):
    mux_signals = []
    for key, val in signals.items():
        if val.mux in mux_signals:
            mux_signals.append(val.mux)

    return mux_signals


def write_dbc(j, dbc, logger):
    logger.info("Writing dbc file")

    spec = Spec()
    spec.decompile(j)

    messages = []
    nodes = []

    for dev_name, dev in spec.devices.items():
        nodes.append(CanNode(dev.name, ""))
        for msg_name, msg in dev.msgs.items():
            id = make_sid(dev.id, msg.id)

            mux_signals = process_mux_signals(msg.signals)
            signals = []
            for sig_name, sig in msg.signals.items():
                for sig in make_signal(sig, mux_signals):
                    signals.append(sig)

            messages.append(CanMessage(id, msg.name, msg.dlc, signals))

    db = CanDatabase(messages=messages, nodes=nodes)
    dump_file(db, dbc)
