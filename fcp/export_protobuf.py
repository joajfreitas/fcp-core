from .specs import Spec, Signal


def conv_signed(signal: Signal):
    if signal.length <= 32:
        return "int32"
    else:
        return "int64"


def conv_unsigned(signal: Signal):
    if signal.length == 1:
        return "bool"
    elif signal.length <= 32:
        return "uint32"
    else:
        return "uint64"


def conv_type(signal: Signal):
    if signal.type == "signed":
        return conv_signed(signal)
    elif signal.type == "unsigned":
        return conv_unsigned(signal)
    elif signal.type == "float":
        return "float"
    elif signal.type == "double":
        return "double"
    else:
        raise ValueError("Unknown signal type: " + signal.type)


def export_protobuf(spec: Spec, output: str):
    def write_device(device):
        ss = ""
        for msg in device.msgs.values():
            ss += "message " + msg.name + " {\n"
            for i, signal in enumerate(msg.signals.values()):
                ss += (
                    "\t"
                    + conv_type(signal)
                    + " "
                    + signal.name
                    + " = "
                    + str(i + 1)
                    + ";\n"
                )
            ss += "}\n\n"

        return ss

    ss = 'edition = "2023";\n\n'
    for device in spec.devices.values():
        ss += write_device(device)

    ss += write_device(spec.common)

    with open(output, "w") as f:
        f.write(ss)
