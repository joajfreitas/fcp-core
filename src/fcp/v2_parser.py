"""V2 parser."""

# Copyright (c) 2024 the fcp AUTHORS.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from beartype.typing import Any, Union, Callable, Tuple, List, Dict
import pathlib
import traceback
import logging

from lark import Lark, Transformer, v_args, UnexpectedCharacters, ParseTree

from .types import Nil, Never

from .specs import struct_field
from .specs import struct
from .specs import enum
from .specs import impl
from .specs import signal_block
from .specs import service
from .specs import rpc
from .specs.type import (
    BuiltinType,
    ArrayType,
    ComposedTypeCategory,
    ComposedType,
    DynamicArrayType,
    Type,
)
from .specs import v2
from .result import Result, Ok, Err
from .maybe import catch
from .specs.metadata import MetaData
from .error_logger import ErrorLogger


fcp_parser = Lark(
    """
    start: preamble (struct | enum | mod_expr | impl | service)*

    preamble: "version" ":" string

    struct: "struct" identifier "{" struct_field+ "}"
    struct_field: identifier "@" number ":" type param* ","
    type: (base_type | array_type | composed_type | dynamic_array_type) "|"?
    base_type: /u\d\d|u\d|i\d\d|i\d|f32|f64|str/
    array_type: "[" type "," number "]"
    dynamic_array_type: "[" type "]"
    composed_type: identifier

    param: identifier "("? param_argument* ")"? "|"?
    param_argument: value ","?

    enum: "enum" identifier "{" enum_field* "}"
    enum_field : identifier "=" value ","

    impl: "impl" identifier "for" identifier "{" (extension_field | signal_block)+ "}"
    signal_block: "signal" identifier "{" extension_field+ "}" ","
    extension_field: identifier ":" value ","

    service: "service" identifier "{" rpc* "}"
    rpc: "rpc" identifier "(" identifier ")"  "returns" identifier

    mod_expr: "mod" identifier ";"

    identifier: CNAME
    string: ESCAPED_STRING
    number: SIGNED_NUMBER
    value : identifier | number | string

    COMMENT: C_COMMENT | CPP_COMMENT

    UNDERSCORE : "_"
    DOT : "."

    %import common.WORD   // imports from terminal library
    %import common.CNAME   // imports from terminal library
    %import common.LETTER   // imports from terminal library
    %import common.DIGIT   // imports from terminal library
    %import common.SIGNED_NUMBER   // imports from terminal library
    %import common.ESCAPED_STRING   // imports from terminal library
    %import common.C_COMMENT // imports from terminal library
    %import common.CPP_COMMENT // imports from terminal library
    %ignore " "           // Disregard spaces in text
    %ignore "\\n"
    %ignore "\\t"
    %ignore COMMENT
    """,
    propagate_positions=True,
)


def _get_meta(tree: ParseTree, parser: Lark) -> MetaData:
    return MetaData(
        line=tree.meta.line,
        end_line=tree.meta.end_line,
        column=tree.meta.column,
        end_column=tree.meta.end_column,
        start_pos=tree.meta.start_pos,
        end_pos=tree.meta.end_pos,
        filename=parser.filename.name,  # type: ignore
    )


def _convert_params(params: Dict[str, Callable]) -> Dict[str, Any]:
    conversion_table = {
        "range": lambda x: {"min_value": x[0], "max_value": x[1]},
        "unit": lambda x: {"unit": x[0]},
    }

    values: Dict[str, Callable] = {}
    for name, value in params.items():
        values.update(conversion_table[name](value))  # type: ignore

    return values


class ParserContext:
    """Retains context during parsing."""

    def __init__(self) -> None:
        self.modules: Dict[str, str] = {}

    def set_module(self, name: str, module: str) -> None:
        """Set the source code module being parsed."""
        self.modules[name] = module

    def get_sources(self) -> Dict[str, str]:
        """Get all the parsed source code modules."""
        return {name: source for name, source in self.modules.items()}


class FcpV2Transformer(Transformer):  # type: ignore
    """Transformer for the Lark AST into the FCP AST."""

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
        """Parse an preamble node of the fcp AST."""
        if args[0] == "3":
            return Ok(None)
        else:
            return Err("Expected IDL version 3")

    def dot(self, args: List[str]) -> str:
        """Parse an dot node of the fcp AST."""
        return "."

    def underscore(self, args: List[str]) -> str:
        """Parse an underscore node of the fcp AST."""
        return "_"

    def identifier(self, args: List[Any]) -> str:
        """Parse an identifier node of the fcp AST."""
        return str(args[0].value)

    def type(self, args: List[str]) -> Type:
        """Parse a type node of the fcp AST."""
        return args[0]

    def base_type(self, args: List[str]) -> BuiltinType:
        """Parse a base_type node of the fcp AST."""
        return BuiltinType(str(args[0]))  # type: ignore

    def array_type(self, args: List[str]) -> ArrayType:
        """Parse an array_type node of the fcp AST."""
        return ArrayType(args[0], int(args[1]))  # type: ignore

    def composed_type(self, args: List[str]) -> ComposedType:
        """Parse a compound_type node of the fcp AST."""
        typename = args[0]

        if self.fcp.get_struct(typename).is_some():
            type_category = ComposedTypeCategory.Struct
        elif self.fcp.get_enum(typename).is_some():
            type_category = ComposedTypeCategory.Enum
        else:
            raise ValueError(f"Type '{typename}' cannot be found.")

        return ComposedType(typename, type_category)  # type: ignore

    def dynamic_array_type(self, args: List[str]) -> DynamicArrayType:
        """Parse a dynamic_array_type of the fcp AST."""
        typename = args[0]

        return DynamicArrayType(typename)  # type: ignore

    def param(self, args: List[str]) -> Tuple[str, ...]:
        """Parse a param node of the fcp AST."""
        return tuple(args)

    def param_argument(self, args: List[str]) -> Any:
        """Parse a param_argument node of the fcp AST."""
        return args[0]

    def field_id(self, args: List[str]) -> Any:
        """Parse a field_id node of the fcp AST."""
        return args[0]

    @v_args(tree=True)  # type: ignore
    def struct(self, tree: ParseTree) -> Never:
        """Parse a struct node of the fcp AST."""
        name, *fields = tree.children

        meta = _get_meta(tree, self)  # type: ignore

        self.fcp.structs.append(
            struct.Struct(
                name=name,
                fields=fields,
                meta=meta,
            )  # type:ignore
        )

    @v_args(tree=True)  # type: ignore
    def struct_field(self, tree: ParseTree) -> struct_field.StructField:
        """Parse a struct_field node of the fcp AST."""
        name, field_id, type, *values = tree.children

        params = {name: value for name, *value in values}  # type: ignore
        params = _convert_params(params)  # type: ignore

        meta = _get_meta(tree, self)  # type: ignore
        return struct_field.StructField(
            name=name,  # type: ignore
            field_id=field_id,  # type: ignore
            type=type,
            meta=meta,
            **params,
        )

    @v_args(tree=True)  # type: ignore
    def enum_field(self, tree: ParseTree) -> enum.Enumeration:
        """Parse an enum_field node of the fcp AST."""
        name, value = tree.children

        meta = _get_meta(tree, self)  # type: ignore

        return enum.Enumeration(name=name, value=value, meta=meta)  # type: ignore

    @v_args(tree=True)  # type: ignore
    def enum(self, tree: ParseTree) -> Never:
        """Parse an enum node of the fcp AST."""
        name, *fields = tree.children

        meta = _get_meta(tree, self)  # type: ignore
        self.fcp.enums.append(
            enum.Enum(name=name, enumeration=fields, meta=meta)  # type: ignore
        )

    @catch
    def mod_expr(self, args: List[str]) -> Result[Nil, str]:
        """Parse a mod_expr node of the fcp AST."""
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
    def impl(self, tree: ParseTree) -> Nil:
        """Parse an impl node of the fcp AST."""

        def is_signal_block(x: Any) -> bool:
            return isinstance(x, signal_block.SignalBlock)

        protocol, name, *fields = tree.children
        type = name  # type and name are the same!

        signal_blocks = [field for field in fields if is_signal_block(field)]
        fields = [field for field in fields if not is_signal_block(field)]

        self.fcp.impls.append(
            impl.Impl(
                name=name,
                protocol=protocol,
                type=type,
                fields=dict(fields),
                signals=signal_blocks,
                meta=_get_meta(tree, self),
            )  # type: ignore
        )

    def extension_field(self, args: List[Any]) -> Tuple[str, Any]:
        """Parse an extension_field node of the fcp AST."""
        name, value = args
        return (name, value)

    @v_args(tree=True)  # type: ignore
    def signal_block(self, tree: ParseTree) -> signal_block.SignalBlock:
        """Parse a signal_block node of the fcp AST."""
        name, *fields = tree.children

        fields: Dict[str, Any] = {field[0]: field[1] for field in fields}  # type: ignore[no-redef]
        return signal_block.SignalBlock(
            name=name, fields=fields, meta=_get_meta(tree, self)
        )  # type: ignore

    @v_args(tree=True)  # type: ignore
    def service(self, tree: ParseTree) -> Nil:
        """Parse a service node of the fcp AST."""
        name, *rpcs = tree.children
        self.fcp.services.append(service.Service(name, rpcs, meta=_get_meta(tree, self)))  # type: ignore

    @v_args(tree=True)  # type: ignore
    def rpc(self, tree: ParseTree) -> str:
        """Parse a rpc node of the fcp AST."""
        name, input, output = tree.children
        return rpc.Rpc(name, input, output, meta=_get_meta(tree, self))  # type: ignore

    def signal_field(self, args: List[Any]) -> Tuple[str, Any]:
        """Parse a signal_field node of the fcp AST."""
        name, value = args
        return (name, value)

    def value(self, args: List[str]) -> Any:
        """Parse a value node of the fcp AST."""
        return args[0]

    def number(self, args: List[str]) -> Union[int, float]:
        """Parse a number node of the fcp AST."""
        try:
            return int(args[0].value)  # type: ignore
        except ValueError:
            return float(args[0].value)  # type: ignore

    def string(self, args: List[str]) -> str:
        """Parse a string node of the fcp AST."""
        return args[0].value[1:-1]  # type: ignore

    def start(self, args: List[str]) -> Result[v2.FcpV2, str]:
        """Parse the start node of the fcp AST."""
        return Ok(self.fcp)


@catch
def get_fcp(fcp_filename: str) -> Result[Tuple[v2.FcpV2, Dict[str, str]], str]:
    """Build a fcp AST from the filename of an fcp schema.

    Returns the Fcp AST and source code information for debugging.
    """
    error_logger = ErrorLogger({})

    with open(fcp_filename) as f:
        source = f.read()
        error_logger.add_source(fcp_filename, source)
        try:
            fcp_ast = fcp_parser.parse(source)
        except UnexpectedCharacters as e:

            return Err(error_logger.log_lark_unexpected_characters(fcp_filename, e))

    parser_context = ParserContext()
    fcp = FcpV2Transformer(fcp_filename, parser_context).transform(fcp_ast).attempt()
    return Ok((fcp, parser_context.get_sources()))
