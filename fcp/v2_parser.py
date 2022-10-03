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

from .specs import (
    Device,
    Broadcast,
    BroadcastSignal,
    Signal,
    Struct,
    Enum,
    Enumeration,
    Comment,
    Command,
    Config,
    Log,
    FcpV2,
)
from .result import Ok, Error, result_shortcut
from .specs.metadata import MetaData
from .verifier import ErrorLogger


def format_lark_exception(exception, filename):
    ss = (
        colored("Error: ", "red", attrs=["bold"])
        + colored("Cannot parse current file", "white", attrs=["bold"])
        + "\n"
    )
    ss += (
        colored(" --> ", "blue", attrs=["bold"])
        + colored(
            f"{filename}:{exception.line}:{exception.column}", "white", attrs=["bold"]
        )
        + "\n"
    )
    ss += exception._format_expected(exception.allowed)

    return ss


fcp_parser = Lark(
    """
    start: (struct | enum | imports)*

    struct: comment* "struct" identifier "{" field+ "}"
    field: comment* identifier ":" param+ ";"
    param: identifier "("? param_argument* ")"? "|"?
    param_argument: value ","?

    enum: comment* "enum" identifier "{" enum_field* "}"
    enum_field : identifier "="? value? ";"

    imports: "import" import_identifier ";"

    import_identifier: (UNDERSCORE|LETTER|DOT) (UNDERSCORE|LETTER|DIGIT|DOT)*
    identifier: CNAME
    string: ESCAPED_STRING
    number: SIGNED_NUMBER
    value : identifier | number | string

    comment : C_COMMENT

    UNDERSCORE : "_"
    DOT : "."

    %import common.WORD   // imports from terminal library
    %import common.CNAME   // imports from terminal library
    %import common.LETTER   // imports from terminal library
    %import common.DIGIT   // imports from terminal library
    %import common.SIGNED_NUMBER   // imports from terminal library
    %import common.ESCAPED_STRING   // imports from terminal library
    %import common.C_COMMENT // imports from terminal library
    %ignore " "           // Disregard spaces in text
    %ignore "\\n"
    %ignore "\\t"
""",
    propagate_positions=True,
)

fpi_parser = Lark(
    """
    start: (broadcast | device | imports | log)*

    broadcast: comment* "broadcast" identifier "{" (field | signal)* "}"
    field: identifier ":" (value) ";"
    value : integer | float | string | identifier
    signal: "signal" identifier "{" field* "}"

    log : comment* "log" identifier "{" field* "}"
    command : comment* "command" identifier "{" field* "}"
    config : comment* "config" identifier "{" field* "}"

    integer: SIGNED_INT
    float: SIGNED_NUMBER
    string: ESCAPED_STRING

    device : "device" identifier "{" (field | command | config)* "}"

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


class Module:
    def __init__(self, filename, children, source, imports):
        self.filename = filename
        self.children = children
        self.source = source
        self.imports = imports

    def __repr__(self):
        return f"{self.filename}: {self.children}"


def get_meta(tree, parser):
    return MetaData(
        line=tree.meta.line,
        end_line=tree.meta.end_line,
        column=tree.meta.column,
        end_column=tree.meta.end_column,
        start_pos=tree.meta.start_pos,
        end_pos=tree.meta.end_pos,
        filename=parser.filename.name,
    )


class FcpV2Transformer(Transformer):
    def __init__(self, filename):
        self.filename = pathlib.Path(filename)
        self.path = self.filename.parent

        with open(self.filename) as f:
            self.source = f.read()

        self.error_logger = ErrorLogger({self.filename: self.source})

    def dot(self, args):
        return "."

    def underscore(self, args):
        return "_"

    def identifier(self, args):
        return args[0]

    def import_identifier(self, args):
        identifier = "".join([arg.value for arg in args])
        return identifier

    def param(self, args):
        return tuple(args)

    def param_argument(self, args):
        return args[0]

    @v_args(tree=True)
    def field(self, tree):
        if isinstance(tree.children[0], Comment):
            comment, name, *values = tree.children
        else:
            name, *values = tree.children
            comment = Comment("")

        type = values[0][0]

        params = {name.value: value for name, value in values[1:]}

        meta = get_meta(tree, self)
        return Ok(Signal(name=name, type=type, meta=meta, comment=comment, **params))

    @v_args(tree=True)
    def struct(self, tree):
        if isinstance(tree.children[0], Comment):
            comment, name, *fields = tree.children
        else:
            name, *fields = tree.children
            comment = Comment("")

        meta = get_meta(tree, self)
        return Ok(
            Struct(
                name=name.value,
                signals=[x.Q() for x in fields],
                meta=meta,
                comment=comment,
            )
        )

    @v_args(tree=True)
    def enum_field(self, tree):
        name, value = tree.children

        meta = get_meta(tree, self)
        return Ok(Enumeration(name=name, value=value, meta=meta))

    @v_args(tree=True)
    def enum(self, tree):
        args = tree.children

        if isinstance(args[0], Comment):
            comment, name, *fields = args
        else:
            name, *fields = args
            comment = Comment("")

        fields = [field.Q() for field in fields]

        meta = get_meta(tree, self)
        return Ok(Enum(name=name, enumeration=fields, meta=meta, comment=comment))

    @result_shortcut
    def imports(self, args):
        filename = self.path / (args[0].replace(".", "/") + ".fcp")
        try:
            with open(filename) as f:
                module = (
                    FcpV2Transformer(filename).transform(fcp_parser.parse(f.read())).Q()
                )
                module.filename = filename.name
        except Exception as e:
            return Error(self.error_logger.error(f"Could not import {filename}"))

        return Ok(module)

    def value(self, args):
        return args[0]

    def number(self, args):
        return int(args[0].value)

    def string(self, args):
        return args[0].value[1:-1]

    def comment(self, args):
        return Comment(args[0].value.replace("/*", "").replace("*/", ""))

    def start(self, args):
        args = [arg.Q() for arg in args]

        imports = list(filter(lambda x: isinstance(x, Module), args))
        not_imports = list(filter(lambda x: not isinstance(x, Module), args))
        return Ok(Module(self.filename.name, not_imports, self.source, imports))


class FpiTransformer(Transformer):
    def __init__(self, filename):
        self.filename = pathlib.Path(filename)
        self.path = self.filename.parent

        with open(self.filename) as f:
            self.source = f.read()

        self.error_logger = ErrorLogger({self.filename: self.source})

    def identifier(self, args):
        return args[0].value

    def value(self, args):
        return args[0]

    def float(self, args):
        return float(args[0].value)

    def integer(self, args):
        return int(args[0].value)

    def string(self, args):
        return args[0].value

    @v_args(tree=True)
    def field(self, tree):
        name, value = tree.children
        return (name, value)

    @v_args(tree=True)
    def signal(self, tree):
        name, *fields = tree.children
        fields = {name: value for name, value in fields}
        meta = get_meta(tree, self)
        return BroadcastSignal(name, fields, meta=meta)

    @v_args(tree=True)
    def broadcast(self, tree):
        if isinstance(tree.children[0], Comment):
            comment, name, *fields = tree.children
        else:
            name, *fields = tree.children
            comment = Comment("")

        signals = filter(lambda x: isinstance(x, BroadcastSignal), fields)
        fields = list(filter(lambda x: not isinstance(x, BroadcastSignal), fields))

        field_names = [field[0] for field in fields]
        if len(field_names) != len(set(field_names)):
            return Error(self.error_logger.error(f"Duplicated key in broadcast {name}"))

        meta = get_meta(tree, self)
        return Ok(
            Broadcast(
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
        filename = args[0] + ".fpi"
        try:
            with open(filename) as f:
                module = FpiTransformer(filename).transform(fpi_parser.parse(f.read()))
                module.filename = filename.name
        except Exception as e:
            return Error(self.error_logger.error(f"Could not import {filename}"))

        return Ok(module)

    @v_args(tree=True)
    def device(self, tree):
        name, *children = tree.children

        fields = filter(lambda x: not isinstance(x, Ok), children)
        fields = {name: value for name, value in fields}

        children = filter(lambda x: isinstance(x, Ok), children)
        children = [child.unwrap() for child in children]

        commands = filter(lambda x: isinstance(x, Command), children)
        configs = filter(lambda x: isinstance(x, Config), children)

        meta = get_meta(tree, self)
        return Ok(
            Device(
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
            Log(
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

        fields = {name: value for name, value in fields}
        meta = get_meta(tree, self)
        return Ok(
            Config(
                name,
                fields["id"],
                fields["type"],
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

        fields = {name: value for name, value in fields}
        meta = get_meta(tree, self)
        return Ok(
            Command(
                name,
                fields.get("n_args"),
                fields["id"],
                [],
                [],
                fields.get("device"),
                comment=comment,
                meta=meta,
            )
        )

    @result_shortcut
    def start(self, args):
        args = [arg.Q() for arg in args]
        imports = list(filter(lambda x: isinstance(x, Module), args))
        not_imports = list(filter(lambda x: not isinstance(x, Module), args))
        return Ok(Module(self.filename.name, not_imports, self.source, imports))


def resolve_imports(module):
    def merge(module1, module2):
        merged = {}
        keys = list(module1.keys()) + list(module2.keys())
        for key in keys:
            merged[key] = module1.get(key) or [] + module2.get(key) or []

        return merged

    nodes = {"enum": [], "struct": [], "broadcast": [], "device": [], "log": []}

    for child in module.children:
        if isinstance(child, Module):
            resolved = resolve_imports(child)
            if resolved.is_err():
                return resolved

            nodes = merge(nodes, resolved.unwrap())
        else:
            child.filename = module.filename

            if child.get_type() not in nodes.keys():
                nodes[child.get_type()] = []

            if child.get_name() in [
                node.get_name() for node in nodes[child.get_type()]
            ]:
                # previous_definition = [node for node in nodes[child.get_type()] if node.get_name() == child.get_name()]
                # print(
                #    f"Error: {child.get_name()} {module.filename}:{child.pos()} already defined."
                # )
                # print(
                #    f"Previously defined in {previous_definition.filename}:{previous_definition.pos()}"
                # )

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
    fpi = {key: fpi[key] for key in fpi.keys() & {"device", "broadcast", "log"}}
    fcp = fcp | fpi
    return Ok(fcp)


def convert(module):
    return Ok(
        FcpV2(
            broadcasts=module["broadcast"].values(),
            devices=module["device"].values(),
            structs=module["struct"].values(),
            enums=module["enum"].values(),
            logs=module["log"].values(),
        )
    )


@result_shortcut
def get_sources(module):
    sources = {module.filename: module.source}
    for mod in module.imports:
        sources = sources | get_sources(mod)

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
                    "Cannot parse current file",
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
    with open(fpi_filename) as f:
        fpi_ast = fpi_parser.parse(f.read())

    fpi = FpiTransformer(fpi_filename).transform(fpi_ast).Q()
    fpi_sources = get_sources(fpi)
    fpi = deduplicate(resolve_imports(fpi).Q()).Q()

    return Ok((convert(merge(fcp, fpi).Q()), fcp_sources | fpi_sources))
