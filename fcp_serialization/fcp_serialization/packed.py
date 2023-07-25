from fcp import Enum, Struct, Broadcast
import math


def get_size(fcp_v2, type):
    if type in fcp_v2.get_builtin_types():
        return int(type[1:])
    elif isinstance(type, str):
        return get_size(fcp_v2, fcp_v2.get_type(type))
    elif isinstance(type, Enum):
        max_value = max([enum.value for enum in type.enumeration])
        if max_value == 0:
            return 1
        else:
            return math.floor(math.log2(max_value)) + 1
    elif isinstance(type, Struct):
        return sum([get_size(fcp_v2, signal.type) for signal in type.signals])
    else:
        raise ValueError(f"{type}")


def allocate_message(fcp_v2, object):
    if isinstance(object, Broadcast):
        struct = fcp_v2.get_type(object.field.get("type"))
    else:
        struct = object
    acc = 0
    for signal in struct.signals:
        size = get_size(fcp_v2, signal.type)
        yield signal.name, acc, size
        acc += size
