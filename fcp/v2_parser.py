import sys
import pathlib
import traceback
from pprint import pprint, pformat

from lark import Lark, Transformer, v_args

from .specs import Device, Broadcast, Signal, Struct, Enum, FcpV2

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
"""
)


class AstNode:
    def __init__(self, type, data, tree):
        self.type = type
        self.data = data
        self.tree = tree
        self.filename = None

    def name(self):
        return self.data["name"]

    def pos(self):
        return self.tree.meta.line, self.tree.meta.column

    def __repr__(self):
        return f"<AstNode {self.type} {self.name()}>"


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
        name, value = tree.children
        # return ({name: value}, tree)
        return Signal(name=name)

    @v_args(tree=True)
    def struct(self, tree):
        name, *fields = tree.children
        return (Struct(name=name, signals=fields), None)

    @v_args(tree=True)
    def enum_field(self, tree):
        name, value = tree.children
        return (name, value, None)

    @v_args(tree=True)
    def enum(self, tree):
        args = tree.children
        name, *fields = args
        return (
            Enum(name=name, enumeration={name: value for name, value, _ in fields}),
            None,
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

        return (module, None)

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
        return ({name: value}, None)

    @v_args(tree=True)
    def broadcast(self, tree):
        name, *fields = tree.children
        fields = {name: value for field in fields for name, value in field[0].items()}
        return (Broadcast(name=name, field=fields), None)

    def imports(self, args):
        filename = args[0] + ".fpi"
        try:
            with open(filename) as f:
                module = FpiTransformer(filename).transform(fpi_parser.parse(f.read()))
        except Exception as e:
            print(f"Could not import {filename}")
            sys.exit(1)

        return (module, None)

    @v_args(tree=True)
    def device(self, tree):
        args = tree.children
        fields, fields_meta = args[1]
        return (Device(name=args[0], id=fields["id"]), None)

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

    for child, _ in module.children:
        if isinstance(child, Module):
            nodes = merge(nodes, resolve_imports(child))
        else:
            child.filename = module.filename

            if child.get_type() not in nodes.keys():
                nodes[child.get_type()] = []

            if child.get_name() in [
                node.get_name() for node in nodes[child.get_type()]
            ]:
                previous_definition = nodes[child.get_type()][child.name()]
                print(
                    f"Error: {child.get_name()} {module.filename}:{child.pos()} already defined."
                )
                print(
                    f"Previously defined in {previous_definition.filename}:{previous_definition.pos()}"
                )
                sys.exit(1)

            nodes[child.get_type()].append(child)

    return nodes


def deduplicate(module):
    return {
        type: {node.get_name(): node for node in module[type]} for type in module.keys()
    }


def merge(fcp, fpi):
    fcp.update(fpi)
    return fcp


def convert(module):
    return FcpV2(
        broadcasts=module["broadcast"].values(),
        devices=module["device"].values(),
        structs=module["struct"].values(),
        enums=module["enum"].values(),
    )


def get_fcp(fcp, fpi):
    fcp_filename = fcp
    with open(fcp_filename) as f:
        ast = fcp_parser.parse(f.read())

    fcp = FcpV2Transformer(fcp_filename).transform(ast)
    fcp = deduplicate(resolve_imports(fcp))

    fpi_filename = fpi
    with open(fpi_filename) as f:
        ast = fpi_parser.parse(f.read())

    fpi = FpiTransformer(fpi_filename).transform(ast)
    fpi = deduplicate(resolve_imports(fpi))

    return convert(merge(fcp, fpi))
