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

"""V2 parser."""

from beartype.typing import Any, Union, Callable, Tuple, List, Dict
import pathlib

from lark import (
    Lark,
    Transformer,
    v_args,
    UnexpectedCharacters,
    UnexpectedEOF,
    ParseTree,
)

from .types import Nil

from .specs import struct_field
from .specs import struct
from .specs import enum
from .specs import impl
from .specs import signal_block
from .specs import service
from .specs import method
from .specs import device
from .specs.type import (
    ArrayType,
    StructType,
    EnumType,
    DynamicArrayType,
    OptionalType,
    StringType,
    UnsignedType,
    SignedType,
    FloatType,
    DoubleType,
    Type,
)
from .specs import v2
from .result import Result, Ok, Err
from .maybe import catch
from .specs.metadata import MetaData
from .error import ErrorLogger, FcpError


fcp_parser = Lark(
    """
    start: preamble (struct | enum | mod_expr | impl | service | device)*

    preamble: "version" ":" string

    struct: "struct" identifier "{" struct_field+ "}"
    struct_field: identifier "@" number ":" type "|"? param* ","
    type: (unsigned_type | signed_type | float_type | double_type | str_type | array_type | composed_type | dynamic_array_type | optional_type)
    str_type: "str"
    unsigned_type: "u" (DIGIT | DIGIT DIGIT)
    signed_type: "i" (DIGIT | DIGIT DIGIT)
    float_type: "f32"
    double_type: "f64"
    array_type: "[" type "," number "]"
    dynamic_array_type: "[" type "]"
    composed_type: identifier
    optional_type: "Optional" "[" type "]"

    param: identifier "("? param_argument* ")"? "|"?
    param_argument: value ","?

    enum: "enum" identifier "{" enum_field* "}"
    enum_field : identifier "=" value ","

    impl: "impl" identifier "for" identifier "as"? identifier? "{" (extension_field | signal_block)+ "}"
    signal_block: "signal" identifier "{" extension_field+ "}" ","
    extension_field: identifier ":" value ","

    service: "service" identifier "@" number "{" method+ "}"
    method: "method" identifier "(" identifier ")" "@" number "returns" identifier

    device: "device" identifier "{" extension_field+ "}"

    mod_expr: "mod" identifier ("." identifier)* ";"

    identifier: CNAME
    string: ESCAPED_STRING
    number: SIGNED_NUMBER
    value : array | identifier | number | string
    array: "[" value ("," value)* "]"

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
        filename=str(parser.filename),
    )


class Token:
    """Metadata stub for any token."""

    def __init__(self, meta: MetaData):
        self.meta = meta


def _convert_params(params: Dict[str, Callable]) -> Dict[str, Any]:
    conversion_table = {
        "range": lambda x: {"min_value": x[0], "max_value": x[1]},
        "unit": lambda x: {"unit": x[0]},
    }

    values: Dict[str, Callable] = {}
    for name, value in params.items():
        values.update(conversion_table[name](value))

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
        return self.modules


class IFileSystemProxy:
    """Filesystem proxy interface."""

    def __init__(self) -> None:
        pass

    def read(self, filename: pathlib.Path) -> str:
        """Read file."""
        raise NotImplementedError


class FileSystemProxy(IFileSystemProxy):
    """Filesystem proxy."""

    def __init__(self) -> None:
        pass

    def read(self, filename: pathlib.Path) -> str:
        """Read file from the filesystem."""
        with open(filename) as f:
            return f.read()


class InMemoryFileSystemProxy(IFileSystemProxy):
    """In-memory filesystem proxy."""

    def __init__(self, files: Dict[pathlib.Path, str]) -> None:
        self.files = files

    def read(self, filename: pathlib.Path) -> str:
        """Read file from the in-memory filesystem."""
        return str(self.files[filename])


class FcpV2Transformer(Transformer):
    """Transformer for the Lark AST into the FCP AST."""

    def __init__(
        self,
        filename: Union[str, pathlib.Path],
        parser_context: ParserContext,
        filesystem_proxy: IFileSystemProxy,
        error_logger: ErrorLogger = ErrorLogger({}),
    ) -> None:
        self.filename = pathlib.Path(filename)
        self.path = self.filename.parent
        self.parser_context = parser_context
        self.error_logger = error_logger
        self.filesystem_proxy = filesystem_proxy
        self.fcp = v2.FcpV2()

        self.source = self.filesystem_proxy.read(self.filename)
        self.parser_context.set_module(self.filename.name, self.source)

    @v_args(tree=True)  # type: ignore
    def preamble(self, tree: ParseTree) -> Result[Nil, FcpError]:
        """Parse an preamble node of the fcp AST."""
        if tree.children[0] == "3":
            return Ok(())
        else:
            return Err(FcpError("Expected IDL version 3", Token(_get_meta(tree, self))))

    def identifier(self, args: List[Any]) -> str:
        """Parse an identifier node of the fcp AST."""
        return str(args[0].value)

    def type(self, args: List[Result[Type, FcpError]]) -> Result[Type, FcpError]:
        """Parse a type node of the fcp AST."""
        return args[0]  # type: ignore

    def unsigned_type(self, args: List[str]) -> Result[UnsignedType, FcpError]:
        """Parse an unsigned type."""
        return Ok(UnsignedType("u" + "".join(args)))

    def signed_type(self, args: List[str]) -> Result[SignedType, FcpError]:
        """Parse a signed type."""
        return Ok(SignedType("i" + "".join(args)))

    def float_type(self, args: List[str]) -> Result[FloatType, FcpError]:
        """Parse a float type."""
        return Ok(FloatType())

    def double_type(self, args: List[str]) -> Result[DoubleType, FcpError]:
        """Parse a double type."""
        return Ok(DoubleType())

    def str_type(self, args: List[str]) -> Result[StringType, FcpError]:
        """Parse a str type."""
        return Ok(StringType())

    @catch
    def array_type(self, args: List[str]) -> Result[ArrayType, FcpError]:
        """Parse an array_type node of the fcp AST."""
        return Ok(
            ArrayType(
                args[0]
                .map_err(lambda err: err.results_in("Error parsing array type"))
                .attempt(),
                int(args[1]),
            )
        )

    @v_args(tree=True)  # type: ignore
    def composed_type(
        self, tree: ParseTree
    ) -> Result[Union[StructType, EnumType], FcpError]:
        """Parse a compound_type node of the fcp AST."""
        typename = tree.children[0]

        if self.fcp.get_struct(typename).is_some():
            return Ok(StructType(typename))
        elif self.fcp.get_enum(typename).is_some():
            return Ok(EnumType(typename))
        else:
            return Err(
                FcpError(
                    f"Type '{typename}' cannot be found.", Token(_get_meta(tree, self))
                )
            )

    def optional_type(self, args: List[str]) -> Result[OptionalType, FcpError]:
        """Parse a option node of the fcp AST."""
        typename = args[0]
        if typename.is_err():
            return Err(typename.err().results_in("Error parsing optional type"))

        return Ok(OptionalType(typename.unwrap()))

    def dynamic_array_type(self, args: List[str]) -> Result[DynamicArrayType, FcpError]:
        """Parse a dynamic_array_type of the fcp AST."""
        typename = args[0]
        if typename.is_err():
            return Err(typename.err().results_in("Error parsing dynamic array type"))

        return Ok(DynamicArrayType(typename.unwrap()))

    def param(self, args: List[str]) -> Tuple[str, ...]:
        """Parse a param node of the fcp AST."""
        return tuple(args)

    def param_argument(self, args: List[str]) -> Any:
        """Parse a param_argument node of the fcp AST."""
        return args[0]

    def field_id(self, args: List[str]) -> Any:
        """Parse a field_id node of the fcp AST."""
        return args[0]

    @catch
    @v_args(tree=True)  # type: ignore
    def struct(self, tree: ParseTree) -> Result[Nil, FcpError]:
        """Parse a struct node of the fcp AST."""
        name, *fields = tree.children

        meta = _get_meta(tree, self)

        self.fcp.structs.append(
            struct.Struct(
                name=name,
                fields=[
                    field.map_err(
                        lambda err: err.results_in(
                            f"Failed to parse field in struct {name}"
                        )
                    ).attempt()
                    for field in fields
                ],
                meta=meta,
            )  # type:ignore
        )

        self.fcp.impls.append(
            impl.Impl(
                name=name,
                protocol="default",
                type=name,
                fields={},
                signals=[],
                meta=meta,
            )
        )

        return Ok(())

    @catch
    @v_args(tree=True)  # type: ignore
    def struct_field(
        self, tree: ParseTree
    ) -> Result[struct_field.StructField, FcpError]:
        """Parse a struct_field node of the fcp AST."""
        name, field_id, type, *values = tree.children

        params = {name: value for name, *value in values}
        params = _convert_params(params)

        meta = _get_meta(tree, self)
        return Ok(
            struct_field.StructField(
                name=name,
                field_id=field_id,
                type=type.map_err(
                    lambda err: err.results_in("Error parsing type in struct field")
                ).attempt(),
                meta=meta,
                **params,
            )
        )

    @v_args(tree=True)  # type: ignore
    def enum_field(self, tree: ParseTree) -> enum.Enumeration:
        """Parse an enum_field node of the fcp AST."""
        name, value = tree.children

        meta = _get_meta(tree, self)

        return enum.Enumeration(name=name, value=value, meta=meta)

    @v_args(tree=True)  # type: ignore
    def enum(self, tree: ParseTree) -> Result[Nil, FcpError]:
        """Parse an enum node of the fcp AST."""
        name, *fields = tree.children

        meta = _get_meta(tree, self)
        self.fcp.enums.append(enum.Enum(name=name, enumeration=fields, meta=meta))

        return Ok(())

    @catch
    @v_args(tree=True)  # type: ignore
    def mod_expr(self, tree: ParseTree) -> Result[Nil, FcpError]:
        """Parse a mod_expr node of the fcp AST."""
        filename = self.path / (".".join(tree.children).replace(".", "/") + ".fcp")

        try:
            with open(filename) as f:
                source = f.read()
        except FileNotFoundError as e:
            return Err(FcpError(f"File not found: {pathlib.Path(e.filename).name}"))

        try:
            self.error_logger.add_source(filename.name, source)
            fcp_ast = fcp_parser.parse(source)
        except (UnexpectedCharacters, UnexpectedEOF) as e:
            return Err(
                FcpError(
                    self.error_logger.log_lark(filename.name, e),
                    Token(
                        MetaData(
                            e.line, e.line, e.column, e.column, 0, 0, str(filename)
                        )
                    ),
                )
            )

        fcp = FcpV2Transformer(
            pathlib.Path(filename).resolve(),
            self.parser_context,
            self.filesystem_proxy,
            self.error_logger,
        ).transform(fcp_ast)

        self.fcp.merge(
            fcp.map_err(
                lambda err: err.results_in(
                    f"Failed to import {filename}", Token(_get_meta(tree, self))
                )
            ).attempt()
        )

        return Ok(())

    @v_args(tree=True)  # type: ignore
    def impl(self, tree: ParseTree) -> Result[Nil, FcpError]:
        """Parse an impl node of the fcp AST."""

        def is_signal_block(x: Any) -> bool:
            return isinstance(x, signal_block.SignalBlock)

        def is_extension_field(x: Any) -> bool:
            return isinstance(x, tuple)

        def is_impl_name(x: Any) -> bool:
            return isinstance(x, str)

        protocol, type, *fields = tree.children
        if len(fields) != 0 and is_impl_name(fields[0]):
            name = fields[0]
            fields = fields[1:]
        else:
            name = type

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
            )
        )

        return Ok(())

    def extension_field(self, args: List[Any]) -> Tuple[str, Any]:
        """Parse an extension_field node of the fcp AST."""
        name, value = args
        return (name, value)

    @v_args(tree=True)  # type: ignore
    def signal_block(self, tree: ParseTree) -> signal_block.SignalBlock:
        """Parse a signal_block node of the fcp AST."""
        name, *fields = tree.children

        return signal_block.SignalBlock(
            name=name,
            fields={field[0]: field[1] for field in fields},
            meta=_get_meta(tree, self),
        )

    @v_args(tree=True)  # type: ignore
    def service(self, tree: ParseTree) -> Result[Nil, FcpError]:
        """Parse a service node of the fcp AST."""
        name, id, *methods = tree.children
        self.fcp.services.append(
            service.Service(name, id, methods, meta=_get_meta(tree, self))
        )

        return Ok(())

    @v_args(tree=True)  # type: ignore
    def method(self, tree: ParseTree) -> method.Method:
        """Parse a method node of the fcp AST."""
        name, input, id, output = tree.children
        return method.Method(name, id, input, output, meta=_get_meta(tree, self))

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
            return int(args[0].value)
        except ValueError:
            return float(args[0].value)

    def string(self, args: List[str]) -> str:
        """Parse a string node of the fcp AST."""
        return str(args[0].value[1:-1])

    def array(self, args: List[Any]) -> List[Any]:
        """Parse an array node of the fcp AST."""
        return args

    @v_args(tree=True)  # type: ignore
    def device(self, tree: ParseTree) -> Result[Nil, FcpError]:
        """Parse a device node of the fcp AST."""
        name, *fields = tree.children
        self.fcp.devices.append(
            device.Device(name, {k: v for k, v in fields}, _get_meta(tree, self))
        )

        return Ok(())

    @catch
    def start(self, args: List[Result[Nil, str]]) -> Result[v2.FcpV2, FcpError]:
        """Parse the start node of the fcp AST."""
        for arg in args:
            arg.map_err(
                lambda err: err.results_in(f"Failed to parse {self.filename.name}")
            ).attempt()

        return Ok(self.fcp)


def _get_fcp(
    filename: pathlib.Path,
    filesystem_proxy: IFileSystemProxy,
    error_logger: ErrorLogger,
) -> Result[Tuple[v2.FcpV2, Dict[str, str]], FcpError]:
    source = filesystem_proxy.read(filename)
    error_logger.add_source(filename.name, source)
    try:
        fcp_ast = fcp_parser.parse(source)
    except UnexpectedCharacters as e:
        return Err(
            FcpError(
                error_logger.log_lark(filename.name, e),
                Token(
                    MetaData(e.line, e.line, e.column, e.column, 0, 0, str(filename))
                ),
            )
        )

    parser_context = ParserContext()

    fcp = FcpV2Transformer(
        filename, parser_context, filesystem_proxy, error_logger
    ).transform(fcp_ast)

    return Ok((fcp.attempt(), parser_context.get_sources()))


@catch
def get_fcp(
    fcp_filename: str, error_logger: ErrorLogger = ErrorLogger({})
) -> Result[Tuple[v2.FcpV2, Dict[str, str]], FcpError]:
    """Build a fcp AST from the filename of an fcp schema.

    Returns the Fcp AST and source code information for debugging.
    """
    filesystem_proxy = FileSystemProxy()
    return _get_fcp(pathlib.Path(fcp_filename), filesystem_proxy, error_logger)


@catch
def get_fcp_from_string(
    source: str, error_logger: ErrorLogger = ErrorLogger({})
) -> Result[Tuple[v2.FcpV2, Dict[str, str]], FcpError]:
    """Build a fcp AST from the source code of an fcp schema."""
    filesystem_proxy = InMemoryFileSystemProxy({pathlib.Path("main.fcp"): source})
    return _get_fcp(pathlib.Path("main.fcp"), filesystem_proxy, error_logger)
