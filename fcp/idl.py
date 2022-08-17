import re
import sys
from pprint import pprint
import traceback

from enum import Enum

from itertools import product

from parsimonious import NodeVisitor
from parsimonious.grammar import Grammar

from jinja2 import Template

from .specs import Spec, Device, Log, Message, Config, Signal, Command

# from .specs import Param


def param_conv(key, value):
    value = [v.strip() for v in value]

    if key == "period":
        yield ("frequency", value[0])
    elif key == "str":
        yield ("string", value[0][1:-1])
    elif key == "start":
        yield ("start", value[0])
    elif key == "length":
        yield ("length", value[0])
    elif key == "sat":
        yield ("min_value", value[0])
        yield ("max_value", value[1])
    elif key == "endianess":
        yield ("byte_order", value[0][1:-1] + "_endian")
    elif key == "mux":
        yield ("mux", value[0][1:-1])
        yield ("mux_count", value[1])
    elif key == "unit":
        yield ("unit", value[0][1:-1])
    elif key == "device":
        yield ("device", value[0][1:-1])
    else:
        yield (key, value[0])


def params_conv(params):
    print("input", params)
    params_spec = {
        "id": {"type": int},
        "dlc": {"type": int},
        "start": {"type": int},
        "length": {"type": int},
        "scale": {"type": float},
        "offset": {"type": float},
        "min_value": {"type": float},
        "max_value": {"type": float},
        "n_args": {"type": int},
        "mux_count": {"type": int},
    }

    def typecast(x):
        name, value = x
        spec = params_spec.get(name)
        if spec is None:
            return (name, value)

        return (name, spec["type"](value))

    params = [
        param for key, value in params.items() for param in param_conv(key, value)
    ]
    params = [typecast(param) for param in params]
    print("output", {param[0]: param[1] for param in params})
    return {param[0]: param[1] for param in params}


class FcpVisitor(NodeVisitor):
    def __init__(self):
        self.types = {}

    def params_conv(self, params):
        params = [param_conv(key, value) for key, value in params.items()]
        params = {k: v for d in params for k, v in d.items()}

        if "type" in params.keys() and params["type"] not in [
            "unsigned",
            "signed",
            "float",
            "double",
        ]:
            t = self.types[params["type"].replace('"', "")]["type"]
            for k, v in t.items():
                params[k] = v

        return params

    def visit_spec(self, node, visited_children):
        d = {
            "log": [],
            "device": [],
            "config": [],
            "command": [],
            "message": [],
            "enum": [],
            "type": [],
        }

        for child in visited_children:
            if child[0] is not None:
                type, child = child[0]
                d[type].append(child)

        # common = d["device"].get("common")
        # if common is not None:
        #    del d["device"]["common"]

        return {
            "logs": d["log"],
            "devices": d["device"],
            "messages": d["message"],
            "configs": d["config"],
            "commands": d["command"],
            "enums": d["enum"],
            "version": "0.3",
        }

    def visit_device(self, node, visited_children):
        _, _, name, _ = visited_children

        return (
            "device",
            {
                "name": name.text.strip(),
            },
        )

    def visit_config(self, node, visited_children):
        comment, _, name, _, params, _ = visited_children
        params = params_conv(params)

        comment = comment[0] if isinstance(comment, list) and comment[0] else ""
        return (
            "config",
            {
                "name": name.text.strip(),
                "comment": comment,
                **params,
            },
        )

    def visit_command(self, node, visited_children):
        comment, _, name, _, params, cmd_args = visited_children
        params = params_conv(params)
        params["id"] = int(params["id"])
        comment = comment[0] if isinstance(comment, list) and comment[0] else ""

        return (
            "command",
            {
                "name": name.text.strip(),
                "args": cmd_args,
                "rets": [],
                "comment": comment,
                **params,
            },
        )

    def visit_cmd_args(self, node, visited_children):
        visited_children = visited_children[0]
        _, args, _ = visited_children

        if type(args) == list:
            return [arg for type, arg in args]
        else:
            return []

    def visit_cmd_arg(self, node, visited_children):
        comment, _, name, _, params, _ = visited_children
        params = params_conv(params)
        comment = comment[0] if isinstance(comment, list) and comment[0] else ""

        return (
            "cmd_arg",
            {
                "comment": comment,
                "name": name.text.strip(),
                **params,
            },
        )

    def visit_message(self, node, visited_children):
        comment, _, name, _, params, _, signals, _ = visited_children

        sigs = [sig for sig in signals]
        # sigs = message_allocation(sigs)

        params = params_conv(params)
        comment = comment[0] if isinstance(comment, list) and comment[0] else ""

        return (
            "message",
            {
                "name": name.text.strip(),
                "signals": sigs,
                "description": comment,  # comment[0],
                **params,
            },
        )

    def visit_signal(self, node, visited_children):
        comment, _, name, _, params, _ = visited_children
        params = params_conv(params)

        comment = comment[0] if isinstance(comment, list) and comment[0] else ""

        return {
            "name": name.text.strip(),
            "comment": comment,  # if comment is None else comment[0],
            **params,
        }

    def visit_params(self, node, visited_children):
        params = {}

        for children in visited_children:
            name, args = children
            params[name] = args

        return params

    def visit_param(self, node, visited_children):
        name, _, args, *_ = visited_children
        name = name.text.strip()
        return name, tuple(args)

    def visit_arg(self, node, visited_children):
        value, *_ = visited_children
        return value[0].text

    def visit_log(self, node, visited_children):
        comment, _, name, _, params, _ = visited_children
        comment = comment[0] if type(comment) == list else ""
        params = params_conv(params)
        return ("log", {"name": name.text.strip(), "comment": comment, **params})

    def visit_enum_value(self, node, visited_children):
        name, _, value, _ = visited_children
        return {
            "name": name.text.strip(),
            "value": value.text.strip(),
        }

    def visit_enum(self, node, visited_children):
        comment, _, name, _, params, _, values, _ = visited_children

        vs = {value["name"]: value for value in values}

        return (
            "enum",
            {
                "name": name.text.strip(),
                "enumeration": vs,
            },
        )

    def visit_comment(self, node, visited_children):
        text, _ = visited_children
        return (
            text.text.replace("/* ", "")
            .replace(" */", "")
            .replace("/*", "")
            .replace("*/", "")
        )

    def visit_type(self, node, visited_children):
        comment, _, _, name, _, arguments, _ = visited_children
        t = {"type": "unsigned", "length": 16, "byte_order": "little_endian"}
        for k, v in arguments:
            t[k] = v

        self.types[name.text.strip()] = {"type": t}
        # return ("type", {"comment": comment.text, "name": name.text, "type": t})

    def visit_argument(self, node, visited_children):
        _, name, _, value, _ = visited_children
        return (name.text, value[0].text)

    def generic_visit(self, node, visited_children):
        """The generic visit method."""
        return visited_children or node


def fcp_v2(file) -> Spec:
    grammar = Grammar(
        """
        spec = (device / message / config / command / log / enum / type)*

        ws        = ~"\s*"
        colon     = ws? ":" ws?
        lbrace    = ws? "{" ws?
        rbrace    = ws? "}" ws?
        pipe      = ws? "|" ws?
        comma     = ws? "," ws?
        lpar      = ws? "(" ws?
        rpar      = ws? ")" ws?
        semicomma = ws? ";" ws?

        name   = ~"[A-Z 0-9\_]*"i
        number = ~"[+-]?([0-9]*[.])?[0-9]+"i
        string = ~'"[^\"]+"'
        catchall = ~"[:%\\"\- A-Z 0-9\.]*"i
        value  = (number / string / catchall)
        comment = ~"\/\*(\*(?!\/)|[^*])*\*\/"i ws?

        arg = value comma? ws?
        param = name lpar arg* rpar pipe?
        params = param*

        device = ws? "device" name semicomma

        message = comment? "message" name colon params lbrace signal* rbrace
        signal = comment? "signal" name colon params semicomma
        command = comment? "command" name colon params cmd_args
        cmd_args = semicomma / (lbrace cmd_arg* rbrace)
        cmd_arg = comment? "arg" name colon params semicomma
        config = comment? "config" name colon params semicomma

        log = comment? "log" name colon params semicomma

        enum = comment? "enum" name colon params lbrace (enum_value)+ rbrace
        enum_value = name colon number semicomma

        argument = ws? name colon (string / number) comma
        type = comment? ws? "type" name lbrace (argument)* rbrace
        """
    )

    fcp_vis = FcpVisitor()
    ast = None
    try:
        ast = grammar.parse(file)
    except Exception as e:
        print(f"exception: {e}")

    try:
        v = fcp_vis.visit(ast)
    except Exception as e:
        print(traceback.format_exc())
        # print(e)
        sys.exit(1)

    return Spec.from_dict(v)
