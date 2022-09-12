import sys
import pathlib
import traceback
from pprint import pprint, pformat

from lark import Lark, Transformer, v_args

from .specs import Device, Broadcast, Signal, Struct, Enum, FcpV2
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
    def __init__(self, filename, children):
        self.filename = filename
        self.children = children

    def __repr__(self):
        return f"{self.filename}: {self.children}"


class FcpV2Transformer(Transformer):
    def __init__(self, filename):
        self.filename = pathlib.Path(filename)
        self.path = self.filename.parent

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
        return Signal(name=name, type=type)

    @v_args(tree=True)
    def struct(self, tree):
        name, *fields = tree.children
        metadata = MetaData(
            line=tree.meta.line, column=tree.meta.column, filename=self.filename.stem
        )
        return Struct(name=name, signals=fields, meta=metadata)

    @v_args(tree=True)
    def enum_field(self, tree):
        name, value = tree.children
        return name, value

    @v_args(tree=True)
    def enum(self, tree):
        args = tree.children
        name, *fields = args
        metadata = MetaData(
            line=tree.meta.line, column=tree.meta.column, filename=self.filename.stem
        )
        return Enum(
            name=name,
            enumeration={name: value for name, value in fields},
            meta=metadata,
        )

    def imports(self, args):
        filename = self.path / (args[0] + ".fcp")
        try:
            with open(filename) as f:
                module = FcpV2Transformer(filename).transform(
                    fcp_parser.parse(f.read())
                )
        except Exception as e:
            print(f"Could not import {filename}")
            print(e)
            print(traceback.format_exc())
            sys.exit(1)

        return module

    def value(self, args):
        return args[0]

    def number(self, args):
        return int(args[0].value)

    def string(self, args):
        return args[0].value

    def start(self, args):
        return Module("__main__", args)


class FpiTransformer(Transformer):
    def __init__(self, filename):
        self.filename = pathlib.Path(filename)
        self.path = self.filename.parent

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
                    print(f"duplicated key: {name} in broadcast {name}")
                    sys.exit(1)
                fs[key] = value

        meta = MetaData(
            line=tree.meta.line, column=tree.meta.column, filename=self.filename.stem
        )
        return Broadcast(name=name, field=fs, meta=meta)

    def imports(self, args):
        filename = args[0] + ".fpi"
        try:
            with open(filename) as f:
                module = FpiTransformer(filename).transform(fpi_parser.parse(f.read()))
        except Exception as e:
            print(f"Could not import {filename}")
            sys.exit(1)

        return module

    @v_args(tree=True)
    def device(self, tree):
        name, *fields = tree.children

        meta = MetaData(
            line=tree.meta.line, column=tree.meta.column, filename=self.filename.stem
        )
        return Device(name=name, id=fields[0]["id"], meta=meta)

    def start(self, args):
        return Module("__main__", args)


def resolve_imports(module):
    def merge(module1, module2):
        merged = {}
        keys = list(module1.keys()) + list(module2.keys())
        for key in keys:
            merged[key] = module1.get(key) or [] + module2.get(key) or []

        return merged

    nodes = {}

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


@result_shortcut
def get_fcp(fcp, fpi):
    fcp_filename = fcp
    with open(fcp_filename) as f:
        fcp_ast = fcp_parser.parse(f.read())

    fcp = FcpV2Transformer(fcp_filename).transform(fcp_ast)
    fcp = deduplicate(resolve_imports(fcp).Q()).Q()

    fpi_filename = fpi
    with open(fpi_filename) as f:
        fpi_ast = fpi_parser.parse(f.read())

    fpi = FpiTransformer(fpi_filename).transform(fpi_ast)
    fpi = deduplicate(resolve_imports(fpi).Q()).Q()

    return convert(merge(fcp, fpi).Q())
