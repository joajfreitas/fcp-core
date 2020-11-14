from typing import *
import copy
import datetime


def handle_key_not_found(d: dict, key: str):
    return d.get(key).items() if d.get(key) != None else []


def field(default_factory):
    return default_factory()


def make_dict():
    return {}


def normalize(xs: Dict[str, Any], key: Callable[[Any], str] = None):
    """ Update xs dictionary keys according to key. 
        By default key is `lambda x : x.name`

    :param xs: Dictionary containing spec node
    :param key: Function that returns the key for a particular node
    """

    if key == None:
        key = lambda x: x.name

    aux = []

    for k, x in xs.items():
        if k != key(x):
            aux.append((k, key(x)))

    for k, key in aux:
        xs[key] = xs[k]
        del xs[k]


class Log:
    """ Log protocol node.

    :param id: Log integer identifier.
    :param name: Name of the Log node.
    :param n_args: Number of arguments in the Log node.
    :param comment: Description of the Log node
    :param string: Display string for the Log node.
    """

    def __init__(
        self,
        parent: "Spec" = None,
        id: int = 0,
        name: str = "",
        n_args: int = 3,
        comment: str = "",
        string: str = "",
    ):
        self.parent = parent
        assert self.parent is not None

        c = max([log.id for log in self.parent.logs.values()]+[0]) + 1
        self.id = id or c
        self.name = name
        self.n_args = n_args
        self.comment = comment
        self.string = string

        self.creation_date = datetime.datetime.now()

    def compile(self) -> Dict[str, Any]:
        """ Transform python class node to its dictionary representation.

        :return: A dictionary containing the node parameters
        """

        d = copy.deepcopy(self.__dict__)
        del d["creation_date"]
        return d

    def decompile(self, d: Dict[str, Any]) -> None:
        """ Transform node dictionary representation into a python class.

        :param d: Node dictionary
        """
        self.__dict__.update(d)

    def get_id(self) -> int:
        return self.id

    def get_name(self) -> str:
        return self.name

    def get_n_args(self) -> int:
        return self.n_args

    def get_comment(self) -> str:
        return self.comment

    def get_string(self) -> str:
        return self.string

    def set_id(self, id: int) -> None:
        try:
            self.id = int(id)
        except Exception as e:
            return

    def set_name(self, name: str) -> None:
        try:
            self.name = name
        except Exception as e:
            return

    def set_n_args(self, n_args: int) -> None:
        try:
            self.n_args = int(n_args)
        except Exception as e:
            return

    def set_comment(self, comment: str) -> None:
        try:
            self.comment = comment
        except Exception as e:
            return

    def set_string(self, string: str) -> None:
        try:
            self.string = string
        except Exception as e:
            return

    def __hash__(self):
        return hash((self.name, self.id, self.creation_date))

    def __repr__(self):
        return "name: {}, id: {}, string: {}, n_args: {}, comment: {}".format(self.name, self.id, self.string, self.n_args, self.comment)

class EnumValue:
    """ Fcp EnumValue. C lookalike for FCP type definitions with name-value
    associations.
    """

    def __init__(self, parent: "Enum" = None) -> None:
        self.parent = parent
        
        assert self.parent is not None

        c = max([value.value for value in self.parent.enumeration.values()] + [0])+1
        self.name = ""
        self.value = c

        self.creation_date = datetime.datetime.now()

    def compile(self) -> Dict[str, Any]:
        d = copy.deepcopy(self.__dict__)
        del d["creation_date"]
        return d

    def decompile(self, d: Dict[str, Any]) -> None:
        """ Transform node dictionary representation into a python class.

        :param d: Node dictionary
        """
        self.__dict__.update(d)
    
    def get_name(self) -> str:
        return self.name

    def set_name(self, name: str) -> None:
        self.name = name

    def get_value(self) -> int:
        return self.value

    def set_value(self, value: int) -> None:
        self.value = int(value)

    def __hash__(self):
        return hash((self.name, self.creation_date))

    def __repr__(self):
        return "name: {}".format(self.name)

class Enum:
    """ Fcp Enum. C lookalike for FCP type definitions with name-value
    associations.
    """

    def __init__(self, parent: "Spec" = None) -> None:
        self.parent = parent
        self.name = ""
        self.enumeration = {}
        self.creation_date = datetime.datetime.now()

    def compile(self) -> Dict[str, Any]:
        enums = {}

        for k, v in self.enumeration.items():
            enums[k] = v.compile()

        d = copy.deepcopy(self.__dict__)
        d["enumeration"] = enums
        del d["creation_date"]
        return d

    def decompile(self, d: Dict[str, Any]) -> None:
        """ Transform node dictionary representation into a python class.

        :param d: Node dictionary
        """
        enumeration = d["enumeration"]
        del d["enumeration"]
        
        self.__dict__.update(d)

        for k,v in enumeration.items():
            enum_value = EnumValue(self)
            enum_value.decompile(v)
            self.enumeration[k] = enum_value
    
    def get_name(self) -> str:
        return self.name

    def set_name(self, name: str) -> None:
        self.name = name

    def get_value(self) -> int:
        return int(self.value)

    def set_value(self, name: int) -> None:
        self.value = int(value)
    
    def normalize(self):
        normalize(self.enumeration)

    def __hash__(self):
        return hash((self.name, self.creation_date))

    def __repr__(self):
        return "name: {}".format(self.name)

class Spec:
    """ FCP root node. Holds all Devices, Messages, Signals, Logs, Configs,
    Commands and Arguments.
    """

    def __init__(self) -> None:
        self.devices = {}
        self.common = Common()
        self.logs = {}
        self.enums = {}
        self.version = "0.2"
        self.parent = None
        self.name = ""
    
    def add_device(self, device: "Device") -> bool:
        """ Add a Device to Spec. 

        :param device: Device to be added
        :return: Operation success status: True - Success, False - Failure
        """
        if device is None:
            return False

        if device.name in self.devices.keys():
            return False

        self.devices[device.name] = device

        return True

    def add_enum(self, enum: "Enum") -> bool:
        """ Add a Enum to Spec. 

        :param enum: Enum to be added
        :return: Operation success status: True - Success, False - Failure
        """

        if enum == None:
            return False

        if enum.name in self.enums.keys():
            return False

        self.enums[enum.name] = enum

        return True

    def add_log(self, log: "Log") -> bool:
        """ Add a Log to Spec. 

        :param log: Log to be added
        :return: Operation success status: True - Success, False - Failure
        """

        if log == None:
            return False

        if log.name in self.logs.keys():
            return False

        self.logs[log.name] = log

        return True
    def get_device(self, name: str) -> Optional["Device"]:
        """ Get a Device from Spec by its name.

        :param name: Device name.
        :return: Device or None if not found.
        """
        return self.devices.get(name)

    def get_log(self, name: str) -> Optional["Log"]:
        """ Get a Log from Spec by its name.

        :param name: Log name.
        :return: Log or None if not found.
        """
        return self.logs.get(name)

    def rm_node(self, node: Any) -> None:
        """ Remove a node from Spec.

        :param node: node to be removed.
        """
        if type(node) == Device:
            self.rm_device(node)
        elif type(node) == Message:
            self.rm_message(node)
        elif type(node) == Signal:
            self.rm_signal(node)
        elif type(node) == Config:
            self.rm_config(node)
        elif type(node) == Command:
            self.rm_cmd(node)
        elif type(node) == Log:
            self.rm_log(node)
        elif type(node) == Enum:
            self.rm_enum(node)
        elif type(node) == EnumValue:
            self.rm_enum_value(node)

    def rm_device(self, device: "Device") -> None:
        """ Remove a Device from Spec.

        :param device: Device to be removed.
        """
        devs = [dev.name for dev in self.devices.values() if dev == device]

        for name in devs:
            del self.devices[name]

    def rm_message(self, message: "Message") -> None:
        """ Remove a Message from Spec.

        :param message: Message to be removed.
        """
        for dev in self.devices.values():
            msgs = []
            for msg in dev.msgs.values():
                if msg == message:
                    msgs.append(msg.name)

            for name in msgs:
                dev.rm_msg(name)

    def rm_signal(self, signal: "Signal") -> None:
        """ Remove a Signal from Spec.

        :param signal: Signal to be removed.
        """


        for dev in self.devices.values():
            for msg in dev.msgs.values():
                signals = []
                for sig in msg.signals.values():
                    if sig is signal:
                        print("found signal")
                        signals.append(signal.name)

                for name in signals:
                    msg.rm_signal(name)

    def rm_config(self, config: "Config") -> None:
        """ Remove a Config from Spec.

        :param config: Config to be removed.
        """


        for dev in self.devices.values():
            cfgs = []
            for cfg in dev.cfgs.values():
                if cfg is config:
                    cfgs.append(cfg.name)

            for name in cfgs:
                dev.rm_cfg(name)

    def rm_cmd(self, command: "Command") -> None:
        """ Remove a Command from Spec.

        :param command: Command to be removed.
        """


        for dev in self.devices.values():
            cmds = []
            for cmd in dev.cfgs.values():
                if cmd is command:
                    cmds.append(cmd)

            for name in cmds:
                dev.rm_cmd(name)

    def rm_log(self, log):
        """ Remove a Log from Spec.

        :param log: Log to be removed.
        """
        logs = []

        for l in self.logs.values():
            if log is l:
                logs.append(l.name)

        for name in logs:
            del self.logs[name]

    def rm_enum(self, enum):
        """ Remove a Enum from Spec.

        :param log: Enum to be removed.
        """
        enums = []

        for l in self.enums.values():
            if enum is l:
                enums.append(l.name)

        for name in enums:
            del self.enums[name]

    def rm_enum_value(self, enum_value):
        """ Remove a Enum from Spec.

        :param log: EnumValue to be removed.
        """

        for e in self.enums.values():
            enum_values = []
            for ev in e.enumeration.values():
                if enum_value is ev:
                    enum_values.append(ev.name)

            for name in enum_values:
                del e.enumeration[name]

    def compile(self) -> Dict[str, Any]:
        """ Transform python class node to its dictionary representation.

        :return: A dictionary containing the node parameters
        """

        d = {"devices": {}, "logs": {}, "enums": {}}

        for dev_k, dev_v in self.devices.items():
            d["devices"][dev_k] = dev_v.compile()

        for log_k, log_v in self.logs.items():
            d["logs"][log_k] = log_v.compile()

        for enum_k, enum_v in self.enums.items():
            d["enums"][enum_k] = enum_v.compile()

        d["common"] = self.common.compile()

        d["version"] = self.version

        return d

    def decompile(self, d: Dict[str, Any]) -> None:
        """ Transform node dictionary representation into a python class.

        :param d: Node dictionary
        """
        d = copy.deepcopy(d)
        self.devices = {}
        self.logs = {}
        self.common.decompile(d["common"])
        
        for k, v in handle_key_not_found(d, "devices"):
            dev = Device(self)
            dev.decompile(v)
            self.devices[k] = dev
        
        for k, v in handle_key_not_found(d, "logs"):
            log = Log(self)
            log.decompile(v)
            self.logs[k] = log
       
        for k, v in handle_key_not_found(d, "enums"):
            enum = Enum(self)
            enum.decompile(v)
            self.enums[k] = enum

        self.versionn = d["version"]

    def normalize(self):
        """ Update devices and logs dictionary keys.  """

        normalize(self.devices)
        normalize(self.logs)

        normalize(self.enums)
        for enum in self.enums.values():
            enum.normalize()

        for key, dev in self.devices.items():
            dev.normalize()

    def __repr__(self):
        out = "Spec: \n"
        for device in self.devices.values():
            out += ""
            out += str(device)
            out += "\n"

        return out


class Signal:
    """ 
    Signal node. Represents a CAN signal, similar to a DBC signal.
            
    :param name: Name of the Signal.
    :param start: Start bit
    :param length: Signal bit size.
    :param scale: Scaling applied to the signal's data.
    :param offset: Offset applied to the signal's data.
    :param unit: Unit of the Signal after applying scaling and offset.
    :param comment: Description of the Signal.
    :param min_value: Minimum value allowed to the Signal's data.
    :param max_value: Maximum value allowed to the Signal's data.
    :param type: Type of the Signal's data.
    :param mux: Name of the mux Signal. None if the Signal doesn't belong to a multiplexed Message.
    :param mux_count: Number of signals that the mux can reference for this Muxed signal.


    """

    def __init__(
        self,
        parent: "Message" = None,
        name: str = "",
        start: int = 0,
        length: int = 0,
        scale: float = 1,
        offset: float = 0,
        unit: str = "",
        comment: str = "",
        min_value: int = 0,
        max_value: int = 0,
        type: str = "unsigned",
        byte_order: str = "little_endian",
        mux: str = "",
        mux_count: int = 1,
        alias: str = "",
    ):
        
        self.parent = parent
        self.name = name
        self.start = start
        self.length = length
        self.scale = scale
        self.offset = offset
        self.unit = unit
        self.comment = comment
        self.min_value = min_value
        self.max_value = max_value
        self.type = type
        self.byte_order = byte_order
        self.mux = mux
        self.mux_count = mux_count
        self.alias = alias

        self.creation_date = datetime.datetime.now()

    def set_name(self, name: str) -> None:
        try:
            self.name = name
        except Exception as e:
            return

    def set_start(self, start: int) -> None:
        try:
            self.start = int(start)
        except Exception as e:
            return

    def set_length(self, length: int) -> None:
        try:
            self.length = int(length)
        except Exception as e:
            return

    def set_scale(self, scale: float) -> None:
        try:
            self.scale = float(scale)
        except Exception as e:
            return

    def set_offset(self, offset: float) -> None:
        try:
            self.offset = float(offset)
        except Exception as e:
            return

    def set_unit(self, unit: str) -> None:
        try:
            self.unit = unit
        except Exception as e:
            return

    def set_comment(self, comment: str) -> None:
        try:
            self.comment = comment
        except Exception as e:
            return

    def set_min_value(self, min_value: float) -> None:
        try:
            self.min_value = float(min_value)
        except Exception as e:
            return

    def set_max_value(self, max_value: float) -> None:
        try:
            self.max_value = float(max_value)
        except Exception as e:
            return

    def set_type(self, type: str) -> None:
        try:
            self.type = type
        except Exception as e:
            return

    def set_byte_order(self, byte_order: str) -> None:
        try:
            self.byte_order = byte_order
        except Exception as e:
            return

    def set_mux(self, mux: str) -> None:
        try:
            self.mux = mux
        except Exception as e:
            return

    def set_mux_count(self, mux_count: int) -> None:
        try:
            self.mux_count = int(mux_count)
        except Exception as e:
            return

    def set_alias(self, alias: str) -> None:
        try:
            self.alias = alias
        except Exception as e:
            return

    def get_name(self) -> str:
        return self.name

    def get_start(self) -> int:
        return self.start

    def get_length(self) -> int:
        return self.length

    def get_scale(self) -> float:
        return self.scale

    def get_offset(self) -> float:
        return self.offset

    def get_unit(self) -> str:
        return self.unit

    def get_comment(self) -> str:
        return self.comment

    def get_min_value(self) -> float:
        return self.min_value

    def get_max_value(self) -> float:
        return self.max_value

    def get_type(self) -> str:
        return self.type

    def get_byte_order(self) -> str:
        return self.byte_order

    def get_mux(self) -> str:
        return self.mux

    def get_mux_count(self) -> int:
        return self.mux_count

    def get_alias(self) -> str:
        return self.alias

    def compile(self) -> Dict[str, Any]:
        """ Transform python class node to its dictionary representation.

        :return: A dictionary containing the node parameters
        """

        d = copy.deepcopy(self.__dict__)
        del d["creation_date"]
        return d

    def decompile(self, d: Dict[str, Any]) -> None:
        """ Transform node dictionary representation into a python class.

        :param d: Node dictionary
        """
        self.__dict__.update(d)

    def __hash__(self):
        return hash((self.name, self.start, self.length, self.creation_date))

#    def __repr__(self):
#        return """ {
#        name: {},
#        start: {}, 
#        length: {}, 
#        scale: {}, 
#        offset: {}, 
#        unit: {}, 
#        comment: {}, 
#        min: {}, 
#        max: {}, 
#        type: {}, 
#        byte_order: {}, 
#        mux: {}, 
#        mux_count: {}
#    }
#    """.format(self.name, self.start, self.length, self.scale, self.offset, self.unit, self.comment, self.min_value, self.max_value, self.type, self.byte_order, self.mux,self.mux_count)

    def __repr__(self):
        return ""


class Message:
    """ Message node, Represents a CAN message, similar to a DBC message.
        
        :param name: Name of the Message.
        :param id: FST Message identifier, highest 6 bits of the identifier.
        :param dlc: Message DLC.
        :param signals: Dictionary containing the Message signals.
        :param frequency: Transmission period in millisecond. If 0 message
        isn't automatically sent. 
    """

    def __init__(
        self,
        parent: "Device" = None,
        name: str = "",
        id: int = 0,
        dlc: int = 8,
        signals: Dict[str, Signal] = None,
        frequency: int = 0,
        description: str = "",
    ):
        
        self.parent = parent
        assert self.parent is not None 
        
        c = max([msg.id for msg in self.parent.msgs.values()] + [0]) + 1
        self.name = name
        self.id = id or c
        self.dlc = dlc
        self.signals = {} if signals == None else signals
        self.frequency = frequency
        self.description = description

        self.creation_date = datetime.datetime.now()

    def set_name(self, name: str) -> None:
        try:
            self.name = name
        except Exception as e:
            return

    def set_id(self, id: int) -> None:
        try:
            self.id = int(id)
        except Exception as e:
            return

    def set_dlc(self, dlc: int) -> None:
        try:
            self.dlc = int(dlc)
        except Exception as e:
            return

    def set_frequency(self, frequency: int) -> None:
        try:
            self.frequency = int(frequency)
        except Exception as e:
            return

    def set_description(self, description: str) -> None:
        try:
            self.description = description
        except Exception as e:
            return

    def get_name(self) -> str:
        return self.name

    def get_id(self) -> int:
        return self.id

    def get_dlc(self) -> int:
        return self.dlc

    def get_frequency(self) -> int:
        return self.frequency

    def get_description(self) -> str:
        return self.description

    def compile(self) -> Dict[str, Any]:
        """ Transform python class node to its dictionary representation.

        :return: A dictionary containing the node parameters
        """

        msgs = {}
        for k, v in self.signals.items():
            msgs[k] = v.compile()

        d = copy.deepcopy(self.__dict__)
        d["signals"] = msgs
        del d["creation_date"]
        return d

    def decompile(self, d: Dict[str, Any]) -> None:
        """ Transform node dictionary representation into a python class.

        :param d: Node dictionary
        """
        signals = d["signals"]
        del d["signals"]

        self.__dict__.update(d)
        for key, value in signals.items():
            sig = Signal(self)
            sig.decompile(value)
            self.signals[key] = sig

    def add_signal(self, signal: Signal) -> bool:
        """ Add a Signal to Message. 

        :param signal: Signal to be added
        :return: Operation success status: True - Success, False - Failure
        """

        if signal == None:
            return False

        if signal.name in self.signals.keys():
            self.signals[signal.name].mux_count += 1
            return True

        self.signals[signal.name] = signal

        return True

    def get_signal(self, name: str) -> Optional[Signal]:
        """ Get a Signal from Message by its name.

        :param name: Signal name.
        :return: Signal or None if not found.
        """

        return self.signals.get(name)

    def rm_signal(self, name: str) -> bool:
        """ Remove a Signal from Spec.

        :param signal: Signal to be removed.
        """
        if self.get_signal(name) is None:
            print("Not found", name)
            return False
        
        print("deleting signal") 
        del self.signals[name]
        return True

    def normalize(self):
        """ Update signals dictionary keys."""

        normalize(self.signals)

    def __hash__(self):
        return hash((self.name, self.id, self.creation_date))

    def __repr__(self):
        return (
            "{"
            + f"""
    name: {self.name}, 
    id: {self.id}, 
    dlc: {self.dlc}, 
    frequency: {self.frequency}
"""
            + "}"
        )


class Argument:
    """ Argument node. Represents a Command Argument.

    :param name: Name of the Argument.
    :param id: Argument identifier.
    :param comment: description of the Argument.
    """

    def __init__(self, parent: "Command" = None, name: str = "", id: int = 0, comment: str = ""):
        self.parent = parent
        self.name = name
        self.id = id
        self.comment = comment

        self.creation_date = datetime.datetime.now()

    def get_name(self) -> str:
        return self.name

    def get_comment(self) -> str:
        return self.comment

    def get_id(self) -> int:
        return self.id

    def set_name(self, name: str) -> None:
        try:
            self.name = name
        except Exception as e:
            return

    def set_comment(self, comment: str) -> None:
        try:
            self.comment = comment
        except Exception as e:
            return

    def set_id(self, id: int) -> None:
        try:
            self.id = int(id)
        except Exception as e:
            return

    def compile(self) -> Dict[str, Any]:
        """ Transform python class node to its dictionary representation.

        :return: A dictionary containing the node parameters
        """
        print("compiling argument")
        d = copy.deepcopy(self.__dict__)
        del d["creation_date"]
        return d

    def decompile(self, d: Dict[str, Any]) -> None:
        """ Transform node dictionary representation into a python class.

        :param d: Node dictionary
        """
        self.__dict__.update(d)


class Command:
    """ Command node. Represents a Command.

    :param name: Name of the Command.
    :param n_args: Number of arguments in the Command.
    :param comment: description of the Command.
    :param id: Command identifier.
    :param args: Dictionary containing the Command's input Arguments.
    :param rets: Dictionary containing the Command's output Arguments.
    """

    def __init__(
        self,
        parent: "Device" = None,
        name: str = "",
        n_args: int = 3,
        comment: str = "",
        id: int = 0,
        args: Dict[str, Argument] = None,
        rets: Dict[str, Argument] = None,
    ):
        
        self.parent = parent
        assert self.parent is not None
        
        c = max([cmd.id for cmd in self.parent.cmds.values()] + [0]) + 1

        self.name = name
        self.n_args = n_args
        self.comment = comment
        self.id = int(id)
        self.args = {} if args == None else args
        self.rets = {} if rets == None else rets

        self.creation_date = datetime.datetime.now()

    def get_name(self) -> str:
        return self.name

    def get_n_args(self) -> int:
        return self.n_args

    def get_comment(self) -> str:
        return self.comment

    def get_id(self) -> int:
        return self.id

    def set_name(self, name: str) -> None:
        try:
            self.name = name
        except Exception as e:
            return

    def set_n_args(self, n_args: int) -> None:
        try:
            self.n_args = int(n_args)
        except Exception as e:
            return

    def set_comment(self, comment: str) -> None:
        try:
            self.comment = comment
        except Exception as e:
            return

    def set_id(self, id: int) -> None:
        try:
            self.id = int(id)
        except Exception as e:
            return

    def compile(self) -> Dict[str, Any]:
        """ Transform python class node to its dictionary representation.

        :return: A dictionary containing the node parameters
        """

        args = {}
        rets = {}

        for k, v in self.args.items():
            args[k] = v.compile()

        for k, v in self.rets.items():
            rets[k] = v.compile()

        att = copy.deepcopy(self.__dict__)
        att["args"] = args
        att["rets"] = rets
        del att["creation_date"]

        return att

    def add_arg(self, arg: Argument) -> None:
        """ Add a input Argument to Command. 

        :param arg: Argument to be added
        :return: Operation success status: True - Success, False - Failure
        """
        self.args[arg.name] = arg

    def add_ret(self, ret: Argument) -> None:
        """ Add a output Argument to Command. 

        :param ret: Argument to be added
        :return: Operation success status: True - Success, False - Failure
        """
        self.rets[ret.name] = ret

    def decompile(self, d: Dict[str, Any]) -> None:
        """ Transform node dictionary representation into a python class.

        :param d: Node dictionary
        """
        args = d["args"]
        rets = d["rets"]
        del d["args"]
        del d["rets"]

        self.__dict__.update(d)
        self.id = int(self.id)
        self.n_args = int(self.n_args)

        for arg_k, arg_v in args.items():
            arg = Argument()
            arg.decompile(arg_v)
            self.args[arg_k] = arg

        for ret_k, ret_v in rets.items():
            ret = Argument()
            ret.decompile(ret_v)
            self.rets[ret_k] = ret

    def normalize(self):
        return

    def __hash__(self):
        return hash((self.name, self.id, self.creation_date))


class Config:
    """ Config node. Represents a Config.

    :param name: Name of the Config.
    :param id: Config identifier.
    :param comment: description of the Config.
    """

    def __init__(self, parent: "Device" = None, name: str = "", id: int = 0, comment: str = ""):
        self.parent = parent
        self.name = name
        self.id = int(id)
        self.comment = comment

        self.creation_date = datetime.datetime.now()

    def get_name(self) -> str:
        return self.name

    def get_id(self) -> int:
        return self.id

    def get_comment(self) -> str:
        return self.comment

    def set_name(self, name: str) -> None:
        try:
            self.name = name
        except Exception as e:
            return

    def set_id(self, id: int) -> None:
        try:
            self.id = int(id)
        except Exception as e:
            return

    def set_comment(self, comment: str) -> None:
        try:
            self.comment = comment
        except Exception as e:
            return

    def compile(self) -> Dict[str, Any]:
        """ Transform python class node to its dictionary representation.

        :return: A dictionary containing the node parameters
        """

        d = copy.deepcopy(self.__dict__)
        del d["creation_date"]
        return d

    def decompile(self, d: Dict[str, Any]) -> None:
        """ Transform node dictionary representation into a python class.

        :param d: Node dictionary
        """
        self.__dict__.update(d)
        self.id = int(self.id)

    def normalize(self):
        return

    def __hash__(self):
        return hash((self.name, self.id, self.creation_date))


class Device:
    """ Device node, Represents a CAN device.
        
        :param name: Name of the Device.
        :param id: FST Device identifier, lowest 5 bits of the identifier.
        :param msgs: Dictionary containing the Device messages.
        :param cmds: Dictionary containing the Device commands.
        :param cfgs: Dictionary containing the Device configs.
        isn't automatically sent. 
    """

    def __init__(
        self,
        parent: "Spec" = None,
        name: str = "default_name",
        id: int = 0,
        msgs: Dict[str, Message] = None,
        cmds: Dict[str, Command] = None,
        cfgs: Dict[str, Config] = None,
    ):
        
        self.parent = parent
        assert self.parent is not None
        c = max([dev.id for dev in self.parent.devices.values()] + [0]) + 1

        self.name = name
        self.id = id or c
        self.msgs = {} if msgs == None else msgs
        self.cmds = {} if cmds == None else cmds
        self.cfgs = {} if cfgs == None else cfgs

        self.creation_date = datetime.datetime.now()

    def set_name(self, name: str) -> None:
        try:
            self.name = name
        except Exception as e:
            return

    def set_id(self, id: int) -> None:
        try:
            self.id = int(id)
        except Exception as e:
            return

    def get_name(self) -> str:
        return self.name

    def get_id(self) -> int:
        return self.id

    def add_cmd(self, cmd: Command) -> None:
        self.cmds[cmd.name] = cmd

    def add_cfg(self, cfg: Config) -> None:
        self.cfgs[cfg.name] = cfg

    def compile(self) -> Dict[str, Any]:
        """ Transform python class node to its dictionary representation.

        :return: A dictionary containing the node parameters
        """

        msgs = {}
        cmds = {}
        cfgs = {}

        for msg_k, msg_v in self.msgs.items():
            msgs[msg_k] = msg_v.compile()

        for cmd_k, cmd_v in self.cmds.items():
            cmds[cmd_k] = cmd_v.compile()

        for cfg_k, cfg_v in self.cfgs.items():
            cfgs[cfg_k] = cfg_v.compile()

        att = copy.deepcopy(self.__dict__)
        att["msgs"] = msgs
        att["cmds"] = cmds
        att["cfgs"] = cfgs
        del att["creation_date"]

        return att

    def decompile(self, d: Dict[str, Any]) -> None:
        """ Transform node dictionary representation into a python class.

        :param d: Node dictionary
        """
        msgs = d["msgs"]
        cmds = d["cmds"]
        cfgs = d["cfgs"]

        del d["msgs"]
        del d["cmds"]
        del d["cfgs"]

        self.__dict__.update(d)

        for k, v in msgs.items():
            msg = Message(self)
            msg.decompile(v)
            self.msgs[k] = msg

        for k, v in cmds.items():
            cmd = Command(self)
            cmd.decompile(v)
            self.cmds[k] = cmd

        for k, v in cfgs.items():
            cfg = Config(self)
            cfg.decompile(v)
            self.cfgs[k] = cfg

    def add_msg(self, msg: Message) -> bool:
        """ Add a Message to Device. 

        :param msg: Message to be added.
        :return: Operation success status: True - Success, False - Failure
        """
        if msg == None:
            return False

        if msg.name in self.msgs.keys():
            return False

        self.msgs[msg.name] = msg

        return True

    def get_msg(self, name: str) -> Optional[Message]:
        """ Get a Message from Device by its name.

        :param name: Message name.
        :return: Message or None if not found.
        """
        return self.msgs.get(name)

    def rm_msg(self, name: str) -> bool:
        """ Remove a Message from Device.

        :param name: Name of the Message to be removed.
        """
        if self.get_msg(name) is None:
            return False

        del self.msgs[name]
        return True

    def get_cmd(self, name: str) -> Optional[Command]:
        """ Get a Command from Device by its name.

        :param name: Command name.
        :return: Command or None if not found.
        """
        return self.cmds.get(name)

    def rm_cmd(self, name: str) -> bool:
        """ Remove a Command from Device.

        :param name: Name of the Command to be removed.
        """
        if self.get_cmd(name) is None:
            return False

        del self.cmds[name]
        return True

    def get_cfg(self, name: str) -> Optional[Config]:
        """ Get a Config from Device by its name.

        :param name: Config name.
        :return: Config or None if not found.
        """
        return self.cfgs.get(name)

    def rm_cfg(self, name: str) -> bool:
        """ Remove a Config from Device.

        :param name: Name of the Config to be removed.
        """
        if self.get_cfg(name) is None:
            return False

        del self.cfgs[name]
        return True

    def normalize(self):
        """ Update messages, commands and configs dictionary keys.  """
        normalize(self.msgs)
        normalize(self.cmds)
        normalize(self.cfgs)

        for key, msg in self.msgs.items():
            msg.normalize()

        for key, cmd in self.cmds.items():
            cmd.normalize()

        for key, cfg in self.cfgs.items():
            cfg.normalize()

    def __hash__(self):
        return hash((self.name, self.id, self.creation_date))

    def __repr__(self):
        return (
            "{"
            + f"""
    name: {self.name}, 
    id: {self.id}
    """
            + "}"
        )


class Common:
    def __init__(
        self,
        parent: Spec = None,
        name: str = "common",
        id: int = 0,
        msgs: Dict[str, Message] = None,
        cfgs: Dict[str, Config] = None,
        cmds: Dict[str, Command] = None,
    ):
        self.parent = parent
        self.name = name
        self.id = id
        self.msgs = {} if msgs == None else msgs
        self.cfgs = {} if cfgs == None else cfgs
        self.cmds = {} if cmds == None else cmds

        self.creation_date = datetime.datetime.now()

    def set_name(self, name: str) -> None:
        try:
            self.name = name
        except Exception as e:
            return

    def set_id(self, id: int) -> None:
        try:
            self.id = int(id)
        except Exception as e:
            return

    def get_name(self) -> str:
        return self.name

    def get_id(self) -> int:
        return self.id

    def add_msg(self, msg: Message) -> bool:
        if msg == None:
            return False

        if msg.name in self.msgs.keys():
            return False

        self.msgs[msg.name] = msg
        return True

    def compile(self) -> Dict[str, Any]:
        """ Transform python class node to its dictionary representation.

        :return: A dictionary containing the node parameters
        """

        msgs = {}
        for msg_k, msg_v in self.msgs.items():
            msgs[msg_k] = msg_v.compile()

        att = copy.deepcopy(self.__dict__)
        att["msgs"] = msgs
        del att["creation_date"]
        return att

    def decompile(self, d: Dict[str, Any]) -> None:
        """ Transform node dictionary representation into a python class.

        :param d: Node dictionary
        """
        msgs = d["msgs"]
        del d["msgs"]

        self.__dict__.update(d)

        for key, value in msgs.items():
            msg = Message(self)
            msg.decompile(value)
            self.msgs[key] = msg

    def __hash__(self):
        return hash((self.name, self.id, self.creation_date))



def make_sid(dev_id: int, msg_id: int) -> int:
    """ Find the sid from the dev_id and the msg_id """
    return msg_id * 32 + dev_id


def decompose_id(sid: int) -> Tuple[int, int]:
    """ Find the dev_id and the msg_id from the sid."""
    return sid & 0x1F, (sid >> 5) & 0x3F
