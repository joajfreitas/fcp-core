import pathlib
import traceback
import logging

from lark import Lark, Transformer, v_args, UnexpectedCharacters, ParseTree
from typing import Any, Union, Callable, Tuple, List, Dict

from serde import from_dict

from .specs import signal
from .specs import struct
from .specs import enum
from .specs import extension
from .specs import signal_block
from .specs.comment import Comment
from .specs import v2
from .result import Ok, Error, result_shortcut
from .specs.metadata import MetaData
from .verifier import ErrorLogger


fcp_parser = Lark(
    """
    start: preamble (struct | enum | imports | extension)*

    preamble: "version" ":" string

    struct: comment* "struct" identifier "{" field+ "}"
    field: comment* identifier field_id ":" param+ ";"
    field_id: "@" number
    param: identifier "("? param_argument* ")"? "|"?
    param_argument: value ","?

    enum: comment* "enum" identifier "{" enum_field* "}"
    enum_field : comment* identifier "="? value? ";"

    extension: identifier "extends" identifier "{" (extension_field | signal_block)+ "}"
    signal_block: "signal" identifier "{" extension_field+ "}" ","
    extension_field: identifier ":" value ","

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
    def __init__(self, filename: str, children: str, source: str, imports: str) -> None:
        self.filename = filename
        self.children = children
        self.source = source
        self.imports = imports

    def __repr__(self) -> str:
        return f"{self.filename}: {self.children}, imports:{len(self.imports)}"


def get_meta(tree: ParseTree, parser: Lark) -> MetaData:
    return MetaData(
        line=tree.meta.line,
        end_line=tree.meta.end_line,
        column=tree.meta.column,
        end_column=tree.meta.end_column,
        start_pos=tree.meta.start_pos,
        end_pos=tree.meta.end_pos,
        filename=parser.filename.name,  # type: ignore
    )


def convert_params(params: Dict[str, Callable]) -> Dict[str, Any]:
    conversion_table = {
        "range": lambda x: {"min_value": x[0], "max_value": x[1]},
        "scale": lambda x: {"scale": x[0], "offset": x[1]},
        "mux": lambda x: {"mux": x[0], "mux_count": x[1]},
        "unit": lambda x: {"unit": x[0]},
        "endianness": lambda x: {"byte_order": x[0]},
    }

    values: Dict[str, Callable] = {}
    for name, value in params.items():
        values.update(conversion_table[name](value))  # type: ignore

    return values


class FcpV2Transformer(Transformer):  # type: ignore
    def __init__(self, filename: str) -> None:
        self.filename = pathlib.Path(filename)
        self.path = self.filename.parent

        with open(self.filename) as f:
            self.source = f.read()

        self.error_logger = ErrorLogger({self.filename.name: self.source})

    def preamble(self, args: List[str]) -> Union[Ok, Error]:
        if args[0] == "3":
            return Ok(None)
        else:
            return Error("Expected IDL version 3")

    def dot(self, args: List[str]) -> str:
        return "."

    def underscore(self, args: List[str]) -> str:
        return "_"

    def identifier(self, args: List[Any]) -> Any:
        return args[0].value

    def import_identifier(self, args: List[str]) -> str:
        identifier = "".join([arg for arg in args])
        return identifier

    def param(self, args: List[str]) -> Tuple[str, ...]:
        return tuple(args)

    def param_argument(self, args: List[str]) -> str:
        return args[0]

    def field_id(self, args: List[str]) -> str:
        return args[0]

    @v_args(tree=True)  # type: ignore
    def field(self, tree: ParseTree) -> Union[Ok, Error]:
        if isinstance(tree.children[0], Comment):
            comment, name, field_id, *values = tree.children
            comment = Comment(comment.value)  # type: ignore
        else:
            name, field_id, *values = tree.children
            comment = None  # type: ignore

        type = values[0][0]  # type: ignore

        params = {name: value for name, *value in values[1:]}  # type: ignore
        params = convert_params(params)  # type: ignore

        meta = get_meta(tree, self)  # type: ignore
        return Ok(
            signal.Signal(
                name=name,  # type: ignore
                type=type,
                field_id=field_id,  # type: ignore
                meta=meta,
                comment=comment,  # type: ignore
                **params,
            )
        )

    @v_args(tree=True)  # type: ignore
    def struct(self, tree: ParseTree) -> Union[Ok, Error]:
        if isinstance(tree.children[0], Comment):
            comment, name, *fields = tree.children
        else:
            name, *fields = tree.children
            comment = None  # type: ignore

        meta = get_meta(tree, self)  # type: ignore
        return Ok(
            struct.Struct(
                name=name,
                signals=[x.Q() for x in fields],  # type: ignore
                meta=meta,
                comment=comment,  # type: ignore
            )
        )

    @v_args(tree=True)  # type: ignore
    def enum_field(self, tree: ParseTree) -> Union[Ok, Error]:
        if isinstance(tree.children[0], Comment):
            comment, name, value = tree.children
        else:
            name, value = tree.children
            comment = None  # type: ignore

        meta = get_meta(tree, self)  # type: ignore

        return Ok(enum.Enumeration(name=name, value=value, comment=comment, meta=meta))  # type: ignore

    @v_args(tree=True)  # type: ignore
    def enum(self, tree: ParseTree) -> Union[Ok, Error]:
        args = tree.children

        if isinstance(args[0], Comment):
            comment, name, *fields = args
        else:
            name, *fields = args
            comment = None  # type: ignore

        fields = [field.Q() for field in fields]  # type: ignore

        meta = get_meta(tree, self)  # type: ignore
        return Ok(enum.Enum(name=name, enumeration=fields, meta=meta, comment=comment))  # type: ignore

    @result_shortcut
    def imports(self, args: List[str]) -> Union[Ok, Error]:
        filename = self.path / (args[0].replace(".", "/") + ".fcp")
        try:
            with open(filename) as f:
                module = (
                    FcpV2Transformer(filename).transform(fcp_parser.parse(f.read())).Q()  # type: ignore
                )
                module.filename = filename.name
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            return Error(self.error_logger.error(f"Could not import {filename}"))

        return Ok(module)

    @result_shortcut
    def extension(self, args: List[Any]) -> Union[Ok, Error]:
        def is_signal_block(x: Any) -> bool:
            return isinstance(x, signal_block.SignalBlock)

        name, type, *fields = args

        signal_blocks = [field for field in fields if is_signal_block(field)]
        fields = [field for field in fields if not is_signal_block(field)]

        return Ok(extension.Extension(name, type, dict(fields), signal_blocks))  # type: ignore

    def extension_field(self, args: List[Any]) -> Tuple[str, Any]:
        name, value = args
        return (name, value)

    def signal_block(self, args: List[Any]) -> signal_block.SignalBlock:
        name, *fields = args

        fields: Dict[str, Any] = {field[0]: field[1] for field in fields}  # type: ignore[no-redef]
        return signal_block.SignalBlock(name, fields)  # type: ignore

    def signal_field(self, args: List[Any]) -> Tuple[str, Any]:
        name, value = args
        return (name, value)

    def value(self, args: List[str]) -> str:
        return args[0]

    def number(self, args: List[str]) -> Union[int, float]:
        try:
            return int(args[0].value)  # type: ignore
        except ValueError:
            return float(args[0].value)  # type: ignore

    def string(self, args: List[str]) -> str:
        return args[0].value[1:-1]  # type: ignore

    def comment(self, args: List[str]) -> Comment:
        return Comment(args[0].value.replace("/*", "").replace("*/", ""))  # type: ignore

    def start(self, args: List[str]) -> Ok:
        args = [arg.Q() for arg in args if arg.Q() is not None]  # type: ignore

        imports = list(filter(lambda x: isinstance(x, Module), args))
        not_imports = list(filter(lambda x: not isinstance(x, Module), args))
        return Ok(Module(self.filename.name, not_imports, self.source, imports))  # type: ignore


def resolve_imports(module: Dict[str, Any]) -> Union[Ok, Error]:
    def merge(module1: Dict, module2: Dict) -> Dict:
        merged = {}
        keys = list(module1.keys()) + list(module2.keys())
        for key in keys:
            merged[key] = (module1.get(key) or []) + (module2.get(key) or [])

        return merged

    nodes: Dict[str, List[Any]] = {
        "enum": [],
        "struct": [],
        "extension": [],
        "log": [],
    }

    for child in module.imports:  # type: ignore
        resolved = resolve_imports(child)
        if resolved.is_err():
            return resolved

        nodes = merge(nodes, resolved.unwrap())  # type: ignore

    for child in module.children:  # type: ignore
        child.filename = module.filename  # type: ignore

        if child.get_type() not in nodes.keys():
            nodes[child.get_type()] = []

        if child.get_name() in [node.get_name() for node in nodes[child.get_type()]]:
            return Error("Duplicated definitions")

        nodes[child.get_type()].append(child)

    return Ok(nodes)


def deduplicate(module: Dict[str, Any]) -> Ok:
    return Ok(
        {
            type: {node.get_name(): node for node in module[type]}
            for type in module.keys()
        }
    )


def convert(module: Dict[str, Any]) -> Ok:
    def to_list(t: type, v: List[Dict[str, Any]]) -> List:
        return [from_dict(t, x) for x in v]

    return Ok(
        v2.FcpV2(  # type: ignore
            structs=to_list(struct.Struct, module["struct"].values()),
            enums=to_list(enum.Enum, module["enum"].values()),
            extensions=to_list(extension.Extension, module["extension"].values()),
            version="3.0",
        )
    )


@result_shortcut
def get_sources(module: Any) -> Dict[str, str]:
    sources = {module.filename: module.source}
    for mod in module.imports:
        sources.update(get_sources(mod))

    return sources


@result_shortcut
def get_fcp(fcp: str) -> Union[Ok, Error]:
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
    fcp = deduplicate(resolve_imports(fcp).Q()).Q()  # type: ignore

    return Ok((convert(fcp), fcp_sources))  # type: ignore
