import pathlib

import lark
from lark import Lark, Transformer

from .result import Ok, Error, result_shortcut
from .verifier import ErrorLogger

from .specs.comment import Comment
from .specs.metadata import MetaData
from .specs.signal import Signal
from .specs.type import Type
from .specs.struct import Struct
from .specs.enum import Enum


fcp_parser = Lark(
    """
    start: preamble (struct | enum | imports)*

    preamble: "version" ":" string ";"

    struct: comment* "struct" identifier "{" field+ "}" ";"
    field: comment* identifier field_id ":" type param* ";"
    field_id: "@" number
    type: (scalar | array)
    scalar: identifier
    array: "[" identifier ";" number "]"

    param: "|" (parameter | parameter_with_args)
    parameter: identifier
    parameter_with_args: identifier "(" param_argument* ")"
    param_argument: value ","?

    enum: comment* "enum" identifier "{" enum_field* "}" ";"
    enum_field : identifier ":" value ";"

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


class Module:
    def __init__(self, filename, children, source, imports):
        self.filename = filename
        self.children = children
        self.source = source
        self.imports = imports

    def __repr__(self):
        return f"{self.filename}: {self.children}, imports:{len(self.imports)}"


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


def convert_params(params):
    convertion_table = {
        "range": lambda x: {"min_value": float(x[0]), "max_value": float(x[1])},
        "scale": lambda x: {"scale": float(x[0]), "offset": float(x[1])},
        "mux": lambda x: {"mux": x[0], "mux_count": x[1]},
        "unit": lambda x: {"unit": x[0]},
        "endianess": lambda x: {"byte_order": x[0]},
    }

    values = {}
    for name, value in params.items():
        values = {**values, **convertion_table[name](value)}

    return values


class FcpV2Transformer(Transformer):
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
            return Error("Expected IDL version 3")

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
        return args[0]

    def parameter(self, args):
        return (args[0],)

    def parameter_with_args(self, args):
        name, *args = args
        return (name.value, *args)

    def param_argument(self, args):
        return args[0]

    def field_id(self, args):
        return args[0]

    def type(self, args):
        return args[0]

    def scalar(self, args):
        return (args[0].value, None)

    def array(self, args):
        type, arity = args
        return (type.value, arity)

    @lark.v_args(tree=True)
    def field(self, tree):
        if isinstance(tree.children[0], Comment):
            comment, name, field_id, type, *values = tree.children
        else:
            name, field_id, type, *values = tree.children
            comment = Comment(value="")

        params = {name: value for name, *value in values}
        params = convert_params(params)

        meta = get_meta(tree, self)
        return Ok(
            Signal(
                name=name.value,
                type=Type(base=type[0], arity=type[1]),
                field_id=field_id,
                meta=meta,
                description=comment,
                **params,
            )
        )

    @lark.v_args(tree=True)
    def struct(self, tree):
        if isinstance(tree.children[0], Comment):
            comment, name, *fields = tree.children
        else:
            name, *fields = tree.children
            comment = None

        meta = get_meta(tree, self)
        return Ok(
            Struct(
                name=name.value,
                signals=[x.Q() for x in fields],
                meta=meta,
                description=comment,
            )
        )

    @lark.v_args(tree=True)
    def enum_field(self, tree):
        name, value = tree.children

        meta = get_meta(tree, self)
        return Ok((name, value, meta))

    @lark.v_args(tree=True)
    def enum(self, tree):
        args = tree.children

        if isinstance(args[0], Comment):
            comment, name, *enum_values = args
        else:
            name, *enum_values = args
            comment = None

        enum_values = {
            enum_value.Q()[0]: (enum_value.Q()[1], enum_value.Q()[2])
            for enum_value in enum_values
        }

        meta = get_meta(tree, self)
        return Ok(
            Enum(name=name, enumeration=enum_values, meta=meta, description=comment)
        )

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
            logging.error(e)
            traceback.print_exc()
            return Error(self.error_logger.error(f"Could not import {filename}"))

        return Ok(module)

    def value(self, args):
        return args[0]

    def number(self, args):
        try:
            return int(args[0].value)
        except ValueError:
            return float(args[0].value)

    def string(self, args):
        return args[0].value[1:-1]

    def comment(self, args):
        return Comment(value=args[0].value.replace("/*", "").replace("*/", ""))

    def start(self, args):
        args = [arg.Q() for arg in args if arg.Q() is not None]

        imports = list(filter(lambda x: isinstance(x, Module), args))
        not_imports = list(filter(lambda x: not isinstance(x, Module), args))
        return Ok(Module(self.filename.name, not_imports, self.source, imports))
