import sys
import pathlib
import traceback
from pprint import pprint, pformat
import logging

from lark import Lark, Transformer, v_args

from .specs import Device, Broadcast, Signal, Struct, Enum, Enumeration, FcpV2
from .result import Ok, Error, result_shortcut
from .specs.metadata import MetaData

fcp_parser = Lark(
    """
    start: (struct | enum | imports)*

    struct: "struct" identifier "{" field+ "}"
    field: identifier ":" param+ ";"
    param: identifier "("? param_argument? ")"? "|"?
    param_argument: value ","?

    enum: "enum" identifier "{" enum_field* "}"
    enum_field : identifier "="? value? ";"

    imports: "import" identifier ";"

    type: identifier
    identifier: string
    string: CNAME
    number: SIGNED_NUMBER
    value : identifier | number

    %import common.WORD   // imports from terminal library
    %import common.CNAME   // imports from terminal library
    %import common.SIGNED_NUMBER   // imports from terminal library
    %ignore " "           // Disregard spaces in text
    %ignore "\\n"
    %ignore "\\t"
""",
    propagate_positions=True,
)

fpi_parser = Lark(
    """
    start: (broadcast | device | imports)*

    broadcast: "broadcast" identifier "{" field* "}"
    field: identifier ":" (value) ";"
    value : integer | string
    integer: SIGNED_NUMBER
    string: CNAME

    device : "device" identifier "{" field* "}"

    imports: "import" identifier ";"

    identifier: CNAME

    %import common.WORD   // imports from terminal library
    %import common.CNAME   // imports from terminal library
    %import common.SIGNED_NUMBER   // imports from terminal library
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

    def identifier(self, args):
        return args[0]

    def type(self, args):
        return args[0]

    def param(self, args):
        return tuple(args)

    def param_argument(self, args):
        return args[0]

    @v_args(tree=True)
    def field(self, tree):
        name, *values = tree.children
        type = values[0][0]

        meta = get_meta(tree, self)
        return Ok(Signal(name=name, type=type, meta=meta))

    @v_args(tree=True)
    def struct(self, tree):
        name, *fields = tree.children

        meta = get_meta(tree, self)
        return Ok(Struct(name=name, signals=[x.Q() for x in fields], meta=meta))

    @v_args(tree=True)
    def enum_field(self, tree):
        name, value = tree.children

        meta = get_meta(tree, self)
        return Ok(Enumeration(name=name, value=value, meta=meta))

    @v_args(tree=True)
    def enum(self, tree):
        args = tree.children
        name, *fields = args

        fields = [field.Q() for field in fields]

        meta = get_meta(tree, self)
        return Ok(
            Enum(
                name=name,
                enumeration=fields,
                meta=meta,
            )
        )

    def imports(self, args):
        filename = self.path / (args[0] + ".fcp")
        try:
            with open(filename) as f:
                module = FcpV2Transformer(filename).transform(
                    fcp_parser.parse(f.read())
                )
                module.filename = filename.name
        except Exception as e:
            return Error(f"Could not import {filename}")

        return Ok(module)

    def value(self, args):
        return args[0]

    def number(self, args):
        return int(args[0].value)

    def string(self, args):
        return args[0].value

    def start(self, args):
        args = [arg.Q() for arg in args]
        imports = list(filter(lambda x: isinstance(x, Module), args))
        not_imports = list(filter(lambda x: not isinstance(x, Module), args))
        return Module(self.filename.name, not_imports, self.source, imports)


class FpiTransformer(Transformer):
    def __init__(self, filename):
        self.filename = pathlib.Path(filename)
        self.path = self.filename.parent

        with open(self.filename) as f:
            self.source = f.read()

    def identifier(self, args):
        return args[0].value

    def value(self, args):
        return args[0]

    def integer(self, args):
        return int(args[0].value)

    def string(self, args):
        return args[0].value

    @v_args(tree=True)
    def field(self, tree):
        name, value = tree.children
        return {name: value}

    @v_args(tree=True)
    def broadcast(self, tree):
        name, *fields = tree.children
        fs = {}
        for field in fields:
            for key, value in field.items():
                if key in fs.keys():
                    return Error(f"duplicated key: {name} in broadcast {name}")
                fs[key] = value

        meta = get_meta(tree, self)
        return Ok(Broadcast(name=name, field=fs, meta=meta))

    def imports(self, args):
        filename = args[0] + ".fpi"
        try:
            with open(filename) as f:
                module = FpiTransformer(filename).transform(fpi_parser.parse(f.read()))
                module.filename = filename.name
        except Exception as e:
            return Error(f"Could not import {filename}")

        return Ok(module)

    @v_args(tree=True)
    def device(self, tree):
        name, *fields = tree.children

        meta = get_meta(tree, self)
        return Ok(Device(name=name, id=fields[0]["id"], meta=meta))

    def start(self, args):
        args = [arg.Q() for arg in args]
        imports = list(filter(lambda x: isinstance(x, Module), args))
        not_imports = list(filter(lambda x: not isinstance(x, Module), args))
        return Module(self.filename.name, not_imports, self.source, imports)


def resolve_imports(module):
    def merge(module1, module2):
        merged = {}
        keys = list(module1.keys()) + list(module2.keys())
        for key in keys:
            merged[key] = module1.get(key) or [] + module2.get(key) or []

        return merged

    nodes = {}

    logging.debug(module.children)
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
    fcp.update(fpi)
    return Ok(fcp)


def convert(module):
    return Ok(
        FcpV2(
            broadcasts=module["broadcast"].values(),
            devices=module["device"].values(),
            structs=module["struct"].values(),
            enums=module["enum"].values(),
        )
    )


def get_sources(module):
    sources = {module.filename: module.source}
    for mod in module.imports:
        sources = sources | get_sources(mod)

    return sources


@result_shortcut
def get_fcp(fcp, fpi):
    fcp_filename = fcp
    with open(fcp_filename) as f:
        fcp_ast = fcp_parser.parse(f.read())

    fcp = FcpV2Transformer(fcp_filename).transform(fcp_ast)
    fcp_sources = get_sources(fcp)
    fcp = deduplicate(resolve_imports(fcp).Q()).Q()

    fpi_filename = fpi
    with open(fpi_filename) as f:
        fpi_ast = fpi_parser.parse(f.read())

    fpi = FpiTransformer(fpi_filename).transform(fpi_ast)
    fpi_sources = get_sources(fpi)
    fpi = deduplicate(resolve_imports(fpi).Q()).Q()

    return convert(merge(fcp, fpi).Q()), fcp_sources | fpi_sources
