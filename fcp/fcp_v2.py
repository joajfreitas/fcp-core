import re
import sys
from pprint import pprint

from enum import Enum

from parsimonious import NodeVisitor
from parsimonious.grammar import Grammar

from jinja2 import Template

from .specs import Device, Log, Message, Config, Signal, Command

def param_conv(key, value):
    value = [v.strip() for v in value]
    if key == "period":
        return {"frequency": value[0]}
    elif key == "str":
        return {"string": value[0]}
    elif key == "size":
        return {"start": value[0], "length": value[1]}
    elif key == "sat":
        return {"min_value": value[0], "max_value": value[1]}
    else:
        return {key: value[0]}
    return {key: value}

def params_conv(params):
    params = [param_conv(key, value) for key, value in params.items()]
    return {k:v for d in params for k,v in d.items()}


class FcpVisitor(NodeVisitor):
    def visit_spec(self, node, visited_children):
        d = {"log": {}, "device": {}}

        for child in visited_children:
            type, child = child[0]
            d[type][child["name"]] = child

        common = d["device"]["common"]
        del d["device"]["common"]

        return {
            "logs": d["log"],
            "devices": d["device"],
            "common": common,
            "version": "0.3",
        }

    def visit_device(self, node, visited_children):
        _, _, name, _, params, _, childs, _ = visited_children

        d = {"config": {}, "message": {}, "command": {}}

        for child in childs:
            type, child = child[0]
            d[type][child["name"]] = child

        params = params_conv(params)

        return (
            "device",
            {
                "name": name.text.strip(),
                "msgs": d["message"],
                "cfgs": d["config"],
                "cmds": d["command"],
                **params,
            }
        )

    def visit_config(self, node, visited_children):
        comment, _, name, _, params, _ = visited_children
        params = params_conv(params)

        return (
            "config",
            {
                "name": name.text.strip(),
                "comment": comment[0],
                **params,
            },
        )

    def visit_command(self, node, visited_children):
        comment, _, name, _, params, cmd_args = visited_children
        params = params_conv(params)

        return (
            "command",
            {
                "name": name.text.strip(),
                "args": {arg["name"]: arg for arg in cmd_args},
                "rets": {},
                "comment": comment[0],
                **params,
            }
        )

    def visit_cmd_args(self, node, visited_children):
        visited_children = visited_children[0]
        _, args, _ = visited_children

        if type(args) == list:
            return [arg for type, arg in args]
        else:
            return []

    def visit_cmd_arg(self, node, visited_children):
        _, _, name, _, params, _ = visited_children
        params = params_conv(params)

        return (
            "cmd_arg",
            {
                "name": name.text.strip(),
                **params,
            }
        )

    def visit_message(self, node, visited_children):
        comment, _, name, _, params, _, signals, _ = visited_children

        sigs = {sig["name"]:sig for sig in signals}

        params = params_conv(params)

        return (
            "message",
            {
                "name": name.text.strip(),
                "signals": sigs,
                "description": comment[0],
                **params,
            }
        )

    def visit_signal(self, node, visited_children):
        comment, _, name, _, params, _ = visited_children
        params = params_conv(params)
        return {
            "name": name.text.strip(),
            "comment": comment[0],
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

        return (
            "log",
            {
                "name": name.text.strip(),
                "comment": comment,
                **params
            }
        )

    def visit_comment(self, node, visited_children):
        text, _ = visited_children
        return text.text.replace("/* ", "").replace(" */", "").replace("/*", "").replace("*/", "")


    def generic_visit(self, node, visited_children):
        """ The generic visit method. """
        return visited_children or node


def fcp_v2(file):
    grammar = Grammar(
        """
        spec = (device / log)*

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

        device = ws? "device" name colon params lbrace (message / command / config)+ rbrace

        message = comment? "message" name colon params lbrace signal* rbrace
        signal = comment? "signal" name colon params semicomma
        command = comment? "command" name colon params cmd_args
        cmd_args = semicomma / (lbrace cmd_arg* rbrace)
        cmd_arg = comment? "arg" name colon params semicomma
        config = comment? "config" name colon params semicomma

        log = comment? "log" name colon params semicomma
        """)

    fcp_vis = FcpVisitor()
    ast = grammar.parse(file)
    return fcp_vis.visit(ast)

def fcp_v2_from_file(file):
    with open(file) as f:
        return fcp_v2(f.read())

def spec_to_fcp_v2(spec):
    template = Template("""
{% for device in devs -%}
device {{device.name}}: id({{device.id}}) {
    {% for msg in device.msgs.values() %}
    /*{{msg.description}}*/
    message {{msg.name}}: id({{msg.id}}) | dlc({{msg.dlc}}) | period({{msg.frequency}}) {
        {% for sig in msg.signals.values() %}
        /*{{sig.comment}}*/
        signal {{sig.name}}: type({{sig.type}}) | size({{sig.start}}, {{sig.length}}) | sat({{sig.min_value}}, {{sig.max_value}});
        {% endfor %}
    }
    {% endfor %}

    {% for cfg in device.cfgs.values() %}
    /*{{cfg.comment}}*/
    config {{cfg.name}}: id({{cfg.id}}) | type({{cfg.type}});
    {% endfor -%}

    {% for cmd in device.cmds.values() %}
    /*{{cmd.comment}}*/
    command {{cmd.name}}: id({{cmd.id}}) {
    {% for arg in cmd.args.values() %}
        /*{{arg.comment}}*/
        arg {{arg.name}}: id({{arg.id}}) | type({{arg.type}});
    {% endfor %}
    {% for ret  in cmd.rets.values() %}
        ret {{arg.name}}: id({{arg.id}}) | type({{arg.type}})
    {% endfor %}
    }
    {% endfor %}
}
{% endfor %}

{% for log in spec.logs.values() %}
log {{log.name}}: id({{log.id}}) | str("{{log.string}}");
{% endfor -%}
""")

    return template.render(
        {
            "spec": spec,
            "devs": list(spec.devices.values()) + [spec.common],
        }
    )
