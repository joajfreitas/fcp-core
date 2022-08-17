import sys
import pathlib
from pprint import pprint, pformat

from lark import Lark, Transformer, v_args

fcp_parser = Lark(
    """
    start: (struct | enum | imports)*

    struct: "struct" identifier "{" field+ "}"
    field: identifier ":" param+ ";"
    param: identifier "("* param_argument* ")"* "|"?
    param_argument: identifier ","?

    enum: "enum" identifier "{" enum_field* "}"
    enum_field : identifier "="? value? ";"

    imports: "import" identifier ";"

    type: identifier
    identifier: CNAME
    value : SIGNED_NUMBER

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
    value : SIGNED_NUMBER | CNAME

    device : "device" identifier ";"

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


class Enum:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields


class Struct:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields


class FcpSpec:
    def __init__(self, types, imports):
        pass


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


class FcpV2Transformer(Transformer):
    def __init__(self, filename):
        self.filename = pathlib.Path(filename)
        self.path = self.filename.parent

    def identifier(self, args):
        return args[0].value

    def type(self, args):
        return args[0]

    def param(self, args):
        return args[0]

    def field(self, args):
        return {"name": args[0], "params": args[1:]}

    @v_args(tree=True)
    def struct(self, tree):
        args = tree.children
        return AstNode("struct", {"name": args[0], "fields": args[1:]}, tree)

    def enum_field(self, args):
        name, value = args
        return {"name": name, "value": value}

    @v_args(tree=True)
    def enum(self, tree):
        args = tree.children
        name, *fields = args
        return AstNode("enum", {"name": name, "fields": fields}, tree)

    def imports(self, args):
        filename = self.path / (args[0] + ".fcp")
        try:
            with open(filename) as f:
                module = FcpV2Transformer(filename).transform(
                    fcp_parser.parse(f.read())
                )
        except Exception as e:
            print(f"Could not import {filename}")
            sys.exit(1)

        return module

    def value(self, args):
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
        return args[0].value

    @v_args(tree=True)
    def field(self, tree):
        name, value = tree.children
        return AstNode("field", {"name": name, "value": value}, tree)

    @v_args(tree=True)
    def broadcast(self, tree):
        name, *fields = tree.children
        return AstNode("broadcast", {"name": name, "fields": fields}, tree)

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
        args = tree.children
        return AstNode("device", {"name": args[0]}, tree)

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
            nodes = merge(nodes, resolve_imports(child))
        else:
            child.filename = module.filename

            if child.type not in nodes.keys():
                nodes[child.type] = []

            if child.name() in [node.name() for node in nodes[child.type]]:
                previous_definition = nodes[child.type][child.name()]
                print(
                    f"Error: {child.name()} {module.filename}:{child.pos()} already defined."
                )
                print(
                    f"Previously defined in {previous_definition.filename}:{previous_definition.pos()}"
                )
                sys.exit(1)

            nodes[child.type].append(child)

    return nodes


def deduplicate(module):
    return {
        type: {node.name(): node for node in module[type]} for type in module.keys()
    }


def merge(fcp, fpi):
    fcp.update(fpi)

    return fcp


class Struct:
    def __init__(self, name, data):
        self.name = name
        self.data = data

    @staticmethod
    def read(node: AstNode):
        return Struct(node.name(), node.data)


class Enum:
    def __init__(self, name, data):
        self.name = name
        self.data = data

    @staticmethod
    def read(node: AstNode):
        return Enum(node.name(), node.data)


class Device:
    def __init__(self, name, data):
        self.name = name

    @staticmethod
    def read(node: AstNode):
        return Device(node.name(), node.data)


class Broadcast:
    def __init__(self, name, data):
        self.name = name
        self.data = data

    @staticmethod
    def read(node: AstNode):
        return Broadcast(node.name(), node.data)

class FcpSpec:
    def __init__(self, fcp):
        self.broadcasts = fcp["broadcast"]
        self.devices = fcp["device"]
        self.structs = fcp["struct"]
        self.enums = fcp["enum"]

    def get_devices(self):
        return self.devices


def convert(module):
    return {
        "broadcast": [Broadcast.read(broadcast) for broadcast in module["broadcast"].values()],
        "device": [Device.read(device) for device in module["device"].values()],
        "struct": [Struct.read(struct) for struct in module["struct"].values()],
        "enum": [Enum.read(enum) for enum in module["enum"].values()],
    }


def get_fcp():
    fcp_filename = sys.argv[1]
    with open(fcp_filename) as f:
        ast = fcp_parser.parse(f.read())

    fcp = FcpV2Transformer(fcp_filename).transform(ast)
    fcp = deduplicate(resolve_imports(fcp))


    fpi_filename = sys.argv[2]
    with open(fpi_filename) as f:
        ast = fpi_parser.parse(f.read())

    fpi = FpiTransformer(fpi_filename).transform(ast)
    fpi = deduplicate(resolve_imports(fpi))

    return FcpSpec(convert(merge(fcp, fpi)))

if __name__ == "__main__":
    pprint(get_fcp())
