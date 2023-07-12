import os
import sys
import pathlib
import traceback
from pprint import pprint, pformat
import logging
from termcolor import colored

from lark import (
    Lark,
    Transformer,
    v_args,
    LarkError,
    UnexpectedInput,
    UnexpectedCharacters,
)

from .specs import signal
from .specs import struct
from .specs import enum
from .specs.comment import Comment
from .specs.type import Type
from .specs import v2
from .result import Ok, Error, result_shortcut
from .specs.metadata import MetaData
from .verifier import ErrorLogger

from .fcp_parser import fcp_parser, FcpV2Transformer


fpi_parser = Lark(
    """
    start: preamble (broadcast | device | imports | log)*

    preamble: "version" ":" string ";"

    broadcast: comment* "broadcast" identifier "{" (field | signal)* "}" ";"
    field: identifier ":" (value) ";"
    value : integer | float | string | identifier
    signal: "signal" identifier "{" field* "}" ";"

    log : comment* "log" identifier ":" param+ ";"
    command : comment* "command" identifier ":" param+ "{"? (cmd_arg | cmd_ret)* "}"? ";"
    cmd_arg: comment* "arg" identifier "@" integer ":" param+ ";"
    cmd_ret: comment* "ret" identifier "@" integer ":" param+ ";"
    config : comment* "config" identifier ":" param+ ";"

    param: identifier param_args?  "|"?
    param_args : "(" param_argument+ ")"
    param_argument: value ","?

    integer: SIGNED_INT
    float: SIGNED_NUMBER
    string: ESCAPED_STRING

    device : "device" identifier ":" param+ "{" (command | config)* "}" ";"

    comment : C_COMMENT
    imports: "import" identifier ";"

    identifier: CNAME

    %import common.WORD
    %import common.CNAME
    %import common.SIGNED_NUMBER
    %import common.ESCAPED_STRING   // imports from terminal library
    %import common.SIGNED_INT
    %import common.C_COMMENT // imports from terminal library
    %ignore " "           // Disregard spaces in text
    %ignore "\\n"
    %ignore "\\t"
""",
    propagate_positions=True,
)


class FpiTransformer(Transformer):
    def __init__(self, filename):
        self.filename = pathlib.Path(filename)
        self.path = self.filename.parent

        with open(self.filename) as f:
            self.source = f.read()

        self.error_logger = ErrorLogger({self.filename: self.source})

    def preamble(self, args):
        if args[0] == "3":
            return Ok(None)
        else:
            return Error(
                self.error_logger.error(
                    f"Expected IDL version 3 [{self.filename.name}]"
                )
            )

    def identifier(self, args):
        return args[0].value

    def value(self, args):
        return args[0]

    def float(self, args):
        return float(args[0].value)

    def integer(self, args):
        return int(args[0].value)

    def string(self, args):
        return args[0].value[1:-1]

    def param(self, args):
        return tuple(args)

    def param_args(self, args):
        return args[0]

    def param_argument(self, args):
        return args[0]

    @v_args(tree=True)
    def field(self, tree):
        name, value = tree.children
        return (name, value)

    @v_args(tree=True)
    def signal(self, tree):
        name, *fields = tree.children
        fields = {name: value for name, value in fields}
        meta = get_meta(tree, self)
        return broadcast.BroadcastSignal(name, fields, meta=meta)

    @v_args(tree=True)
    def broadcast(self, tree):
        if isinstance(tree.children[0], Comment):
            comment, name, *fields = tree.children
        else:
            name, *fields = tree.children
            comment = Comment("")

        signals = filter(lambda x: isinstance(x, broadcast.BroadcastSignal), fields)
        fields = list(
            filter(lambda x: not isinstance(x, broadcast.BroadcastSignal), fields)
        )

        field_names = [field[0] for field in fields]
        if len(field_names) != len(set(field_names)):
            return Error(self.error_logger.error(f"Duplicated key in broadcast {name}"))

        meta = get_meta(tree, self)
        return Ok(
            broadcast.Broadcast(
                name=name,
                field={name: value for name, value in fields},
                signals=signals,
                meta=meta,
                comment=comment,
            )
        )

    def comment(self, args):
        return Comment(args[0].value.replace("/*", "").replace("*/", ""))

    def imports(self, args):
        filename = self.path / (args[0] + ".fpi")
        try:
            with open(filename) as f:
                module = (
                    FpiTransformer(filename).transform(fpi_parser.parse(f.read())).Q()
                )
                module.filename = filename.name
        except Exception as e:
            # logging.error(e)
            traceback.print_exc()
            return Error(self.error_logger.error(f"Could not import {filename}\n{e}"))

        return Ok(module)

    @v_args(tree=True)
    def device(self, tree):
        name, *children = tree.children

        fields = filter(lambda x: not isinstance(x, Ok), children)
        fields = {name: value for name, value in fields}

        children = filter(lambda x: isinstance(x, Ok), children)
        children = [child.unwrap() for child in children]

        commands = filter(lambda x: isinstance(x, cmd.Command), children)
        configs = filter(lambda x: isinstance(x, config.Config), children)

        meta = get_meta(tree, self)
        return Ok(
            device.Device(
                name=name,
                id=fields["id"],
                commands=commands,
                configs=configs,
                meta=meta,
            )
        )

    @v_args(tree=True)
    def log(self, tree):
        if isinstance(tree.children[0], Comment):
            comment, name, *fields = tree.children
        else:
            name, *fields = tree.children
            comment = Comment("")

        meta = get_meta(tree, self)
        fields = {name: value for name, value in fields}

        n_args = fields.get("n_args") or 0
        return Ok(
            log.Log(
                id=fields["id"],
                name=name,
                comment=comment,
                string=fields["str"],
                n_args=n_args,
                meta=meta,
            )
        )

    @v_args(tree=True)
    def config(self, tree):
        if isinstance(tree.children[0], Comment):
            comment, name, *fields = tree.children
        else:
            name, *fields = tree.children
            comment = Comment("")

        type = fields[0][0]
        fields = {name: value for name, value in fields[1:]}
        meta = get_meta(tree, self)
        return Ok(
            config.Config(
                name,
                fields["id"],
                type,
                fields["device"],
                comment=comment,
                meta=meta,
            )
        )

    @v_args(tree=True)
    def command(self, tree):
        if isinstance(tree.children[0], Comment):
            comment, name, *fields = tree.children
        else:
            name, *fields = tree.children
            comment = Comment("")

        args = [field for field in fields if isinstance(field, cmd.CommandArg)]
        rets = [field for field in fields if isinstance(field, cmd.CommandRet)]
        fields = [field for field in fields if isinstance(field, tuple)]

        fields = {name: value for name, value in fields}
        meta = get_meta(tree, self)
        return Ok(
            cmd.Command(
                name,
                fields["id"],
                args,
                rets,
                fields.get("device"),
                comment=comment,
                meta=meta,
            )
        )

    @v_args(tree=True)
    def cmd_arg(self, tree):
        if isinstance(tree.children[0], Comment):
            comment, name, id, *params = tree.children
        else:
            name, id, *params = tree.children
            comment = Comment("")

        type, *params = params
        return cmd.CommandArg(name=name, type=type[0], id=id)

    @v_args(tree=True)
    def cmd_ret(self, tree):
        if isinstance(tree.children[0], Comment):
            comment, name, id, *params = tree.children
        else:
            name, id, *params = tree.children
            comment = Comment("")

        type, *params = params
        return cmd.CommandRet(name=name, type=type[0], id=id)

    @result_shortcut
    def start(self, args):
        args = [arg.Q() for arg in args if arg.Q() is not None]

        imports = list(filter(lambda x: isinstance(x, Module), args))
        not_imports = list(filter(lambda x: not isinstance(x, Module), args))

        return Ok(Module(self.filename.name, not_imports, self.source, imports))


def resolve_imports(module):
    def merge(module1, module2):
        merged = {}
        keys = list(module1.keys()) + list(module2.keys())
        for key in keys:
            merged[key] = (module1.get(key) or []) + (module2.get(key) or [])

        return merged

    nodes = {"enum": [], "struct": []}

    for child in module.imports:
        resolved = resolve_imports(child)
        if resolved.is_err():
            return resolved

        nodes = merge(nodes, resolved.unwrap())

    for child in module.children:
        child.meta.filename = module.filename

        if child.get_type() not in nodes.keys():
            nodes[child.get_type()] = []

        if child.get_name() in [node.get_name() for node in nodes[child.get_type()]]:
            return Error("Duplicated definitions")

        nodes[child.get_type()].append(child)

    return Ok(nodes)


def deduplicate(module):
    return Ok(
        {
            type: {node.get_name(): node for node in module[type]}
            for type in module.keys()
        }
    )


def merge(fcp, fpi):
    fcp = {key: fcp[key] for key in fcp.keys() & {"struct", "enum"}}
    fpi = (
        {"broadcast": {}, "device": {}, "log": {}}
        if not fpi
        else {key: fpi[key] for key in fpi.keys() & {"device", "broadcast", "log"}}
    )
    fcp = {**fcp, **fpi}
    return Ok(fcp)


def convert(module):
    return Ok(
        v2.FcpV2(
            structs=list(module["struct"].values()),
            enums=list(module["enum"].values()),
        )
    )


@result_shortcut
def get_sources(module):
    sources = {module.filename: module.source}
    for mod in module.imports:
        sources = {**sources, **get_sources(mod)}

    return sources


@result_shortcut
def get_fcp(fcp, fpi):
    error_logger = ErrorLogger({})
    fcp_filename = fcp

    with open(fcp_filename) as f:
        try:
            source = f.read()
            error_logger.add_source(fcp_filename, source)
            fcp_ast = fcp_parser.parse(source)
        except UnexpectedCharacters as e:
            return Error(
                error_logger.log_surrounding(
                    f"Cannot parse current file: {fcp_filename}:{e.line}:{e.column}",
                    fcp_filename,
                    e.line,
                    e.column,
                    e._format_expected(e.allowed),
                )
            )

    fcp = FcpV2Transformer(fcp_filename).transform(fcp_ast).Q()
    fcp_sources = get_sources(fcp)
    fcp = deduplicate(resolve_imports(fcp).Q()).Q()

    fpi_filename = fpi
    if fpi_filename:
        with open(fpi_filename) as f:
            fpi_ast = fpi_parser.parse(f.read())

        fpi = FpiTransformer(fpi_filename).transform(fpi_ast).Q()
        fpi_sources = get_sources(fpi)
        fpi = deduplicate(resolve_imports(fpi).Q()).Q()
    else:
        fpi_sources = {}

    return Ok((convert(merge(fcp, fpi).Q()), {**fcp_sources, **fpi_sources}))
