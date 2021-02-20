from typing import *
import datetime

from .node import Node, Transmit
from .arg import Argument
from ..can import CANMessage

class Command(Transmit):
    """Command node. Represents a Command.

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

        c = max([int(cmd.id) for cmd in self.parent.cmds.values()] + [0]) + 1

        self._name = name
        self._n_args = n_args
        self._comment = comment
        self._id = int(id)
        self.args = {} if args == None else args
        self.rets = {} if rets == None else rets

        self.creation_date = datetime.datetime.now()

    @property
    def name(self) -> str:
        return self._name

    @property
    def n_args(self) -> int:
        return int(self._n_args)

    @property
    def comment(self) -> str:
        return self._comment

    @property
    def id(self) -> int:
        return int(self._id)

    @name.setter
    def name(self, name: str) -> None:
        try:
            self._name = name
        except Exception as e:
            return

    @n_args.setter
    def n_args(self, n_args: int) -> None:
        try:
            self._n_args = int(n_args)
        except Exception as e:
            return

    @comment.setter
    def comment(self, comment: str) -> None:
        try:
            self._comment = comment
        except Exception as e:
            return

    @id.setter
    def id(self, id: int) -> None:
        try:
            self._id = int(id)
        except Exception as e:
            return

    def compile(self) -> Dict[str, Any]:
        """Transform python class node to its dictionary representation.

        :return: A dictionary containing the node parameters
        """

        args = {}
        rets = {}

        for k, v in self.args.items():
            args[k] = v.compile()

        for k, v in self.rets.items():
            rets[k] = v.compile()

        att = self.make_public(self, self.filter_private(self.__dict__))
        att["args"] = args
        att["rets"] = rets

        return att

    def add_arg(self, arg: Argument) -> None:
        """Add a input Argument to Command.

        :param arg: Argument to be added
        :return: Operation success status: True - Success, False - Failure
        """
        self.args[arg.name] = arg

    def add_ret(self, ret: Argument) -> None:
        """Add a output Argument to Command.

        :param ret: Argument to be added
        :return: Operation success status: True - Success, False - Failure
        """
        self.rets[ret.name] = ret

    def decompile(self, d: Dict[str, Any]) -> None:
        """Transform node dictionary representation into a python class.

        :param d: Node dictionary
        """
        args = d["args"]
        rets = d["rets"]

        #self.__dict__.update(make_private(self, d))
        for k,v in self.make_private(self, d).items():
            self.__setattr__(k,v)

        for arg_k, arg_v in args.items():
            arg = Argument()
            arg.decompile(arg_v)
            self.args[arg_k] = arg

        for ret_k, ret_v in rets.items():
            ret = Argument()
            ret.decompile(ret_v)
            self.rets[ret_k] = ret

    def encode(self, src: int, dst: int, args) -> CANMessage:
        common = self.parent.parent.get_common()
        send_cmd = common.get_msg("send_cmd")
        msg = send_cmd.encode(
            {"id": self.id, "dst": dst, "arg1": args[0], "arg2": args[1], "arg3": args[2]},
            src=src
        )
        return msg

    def is_cmd(self, msg: CANMessage) -> bool:
        common = self.parent.parent.get_common()
        send_cmd = common.get_msg("send_cmd")
        return msg.get_msg_id() == send_cmd.id

    def __repr__(self):
        return f"<Cmd name={self.name} id={self.id}>"

    def __hash__(self):
        return hash((self.name, self.id, self.creation_date))
