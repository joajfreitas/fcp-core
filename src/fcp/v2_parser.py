from beartype.typing import Any, Union, Callable, Tuple, List, Dict
import pathlib
import traceback
import logging

from lark import Lark, Transformer, v_args, UnexpectedCharacters, ParseTree

from .types import Nil, Never

from .specs import signal
from .specs import struct
from .specs import enum
from .specs import extension
from .specs import signal_block
from .specs.comment import Comment
from .specs import v2
from .result import Result, Ok, Err
from .maybe import catch
from .specs.metadata import MetaData
from .error_logger import ErrorLogger


fcp_parser = Lark(
    """
    start: preamble (struct | enum | mod_expr | extension)*

    preamble: "version" ":" string

    struct: comment* "struct" identifier "{" field+ "}"
    field: comment* identifier "@" number ":" param+ ","
    param: identifier "("? param_argument* ")"? "|"?
    param_argument: value ","?

    enum: comment* "enum" identifier "{" enum_field* "}"
    enum_field : comment* identifier "="? value? ","

    extension: identifier identifier "extends" identifier "{" (extension_field | signal_block)+ "}"
    signal_block: "signal" identifier "{" extension_field+ "}" ","
    extension_field: identifier ":" value ","

    mod_expr: "mod" identifier ";"

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
        self.source = source

    def __repr__(self) -> str:
        return f"Module {self.filename}"


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


class ParserContext:
    def __init__(self) -> None:
        self.modules: Dict[str, str] = {}

    def set_module(self, name: str, module: str) -> None:
        self.modules[name] = module

    def get_sources(self) -> Dict[str, str]:
        return {name: source for name, source in self.modules.items()}


class FcpV2Transformer(Transformer):  # type: ignore
    def __init__(
        self, filename: Union[str, pathlib.Path], parser_context: ParserContext
    ) -> None:
        self.filename = pathlib.Path(filename)
        self.path = self.filename.parent
        self.parser_context = parser_context
        self.fcp = v2.FcpV2()

        with open(self.filename) as f:
            self.source = f.read()

        self.parser_context.set_module(self.filename.name, self.source)
        self.error_logger = ErrorLogger({self.filename.name: self.source})

    def preamble(self, args: List[str]) -> Result[None, str]:
        if args[0] == "3":
            return Ok(None)
        else:
            return Err("Expected IDL version 3")

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

    def param_argument(self, args: List[str]) -> Any:
        return args[0]

    def field_id(self, args: List[str]) -> Any:
        return args[0]

    @v_args(tree=True)  # type: ignore
    def field(self, tree: ParseTree) -> signal.Signal:
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
        return signal.Signal(
            name=name,  # type: ignore
            field_id=field_id,  # type: ignore
            type=type,
            meta=meta,
            comment=comment,  # type: ignore
            **params,
        )

    @v_args(tree=True)  # type: ignore
    def struct(self, tree: ParseTree) -> Never:
        if isinstance(tree.children[0], Comment):
            comment, name, *fields = tree.children
        else:
            name, *fields = tree.children
            comment = None  # type: ignore

        meta = get_meta(tree, self)  # type: ignore

        self.fcp.structs.append(
            struct.Struct(
                name=name,
                signals=fields,
                meta=meta,
                comment=comment,  # type: ignore
            )
        )

    @v_args(tree=True)  # type: ignore
    def enum_field(self, tree: ParseTree) -> enum.Enumeration:
        if isinstance(tree.children[0], Comment):
            comment, name, value = tree.children
        else:
            name, value = tree.children
            comment = None  # type: ignore

        meta = get_meta(tree, self)  # type: ignore

        return enum.Enumeration(name=name, value=value, comment=comment, meta=meta)  # type: ignore

    @v_args(tree=True)  # type: ignore
    def enum(self, tree: ParseTree) -> Never:
        args = tree.children

        if isinstance(args[0], Comment):
            comment, name, *fields = args
        else:
            name, *fields = args
            comment = None  # type: ignore

        meta = get_meta(tree, self)  # type: ignore
        self.fcp.enums.append(
            enum.Enum(name=name, enumeration=fields, meta=meta, comment=comment)  # type: ignore
        )

    @catch
    def mod_expr(self, args: List[str]) -> Result[Nil, str]:
        filename = self.path / (args[0].replace(".", "/") + ".fcp")

        try:
            with open(filename) as f:
                source = f.read()
                fcp = (
                    FcpV2Transformer(filename, self.parser_context)
                    .transform(fcp_parser.parse(source))
                    .attempt()
                )

                self.fcp.merge(fcp)

        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            return Err(self.error_logger.error(f"Could not import {filename}"))

        return Ok(())

    @v_args(tree=True)  # type: ignore
    def extension(self, tree: ParseTree) -> Nil:
        def is_signal_block(x: Any) -> bool:
            return isinstance(x, signal_block.SignalBlock)

        protocol, name, type, *fields = tree.children

        signal_blocks = [field for field in fields if is_signal_block(field)]
        fields = [field for field in fields if not is_signal_block(field)]

        self.fcp.extensions.append(
            extension.Extension(
                name=name,
                protocol=protocol,
                type=type,
                fields=dict(fields),
                signals=signal_blocks,
                meta=get_meta(tree, self),
            )  # type: ignore
        )

    def extension_field(self, args: List[Any]) -> Tuple[str, Any]:
        name, value = args
        return (name, value)

    @v_args(tree=True)  # type: ignore
    def signal_block(self, tree: ParseTree) -> signal_block.SignalBlock:
        name, *fields = tree.children

        fields: Dict[str, Any] = {field[0]: field[1] for field in fields}  # type: ignore[no-redef]
        return signal_block.SignalBlock(
            name=name, fields=fields, meta=get_meta(tree, self)
        )  # type: ignore

    def signal_field(self, args: List[Any]) -> Tuple[str, Any]:
        name, value = args
        return (name, value)

    def value(self, args: List[str]) -> Any:
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

    def start(self, args: List[str]) -> Result[v2.FcpV2, str]:
        return Ok(self.fcp)


@catch
def get_fcp(fcp_filename: pathlib.Path) -> Result[Tuple[v2.FcpV2, Dict[str, str]], str]:
    error_logger = ErrorLogger({})

    with open(fcp_filename) as f:
        source = f.read()
        error_logger.add_source(fcp_filename.name, source)
        try:
            fcp_ast = fcp_parser.parse(source)
        except UnexpectedCharacters as e:
            return Err(
                error_logger.log_lark_unexpected_characters(fcp_filename.name, e)
            )

    parser_context = ParserContext()
    fcp = FcpV2Transformer(fcp_filename, parser_context).transform(fcp_ast).attempt()
    return Ok((fcp, parser_context.get_sources()))
