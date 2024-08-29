import pathlib
import traceback
import logging

from lark import Lark, Transformer, v_args, UnexpectedCharacters, ParseTree
from typing import Any, Union, Callable, Tuple

from lark.lexer import Token
from lark.tree import Branch
from serde import from_dict

from .specs import device
from .specs import broadcast
from .specs import signal
from .specs import struct
from .specs import enum
from .specs.comment import Comment
from .specs import cmd
from .specs import config
from .specs import log
from .specs import v2
from .result import Ok, Error, result_shortcut
from .specs.metadata import MetaData
from .verifier import ErrorLogger


fcp_parser = Lark(
    """
    start: preamble (struct | enum | imports)*

    preamble: "version" ":" string

    struct: comment* "struct" identifier "{" field+ "}" ";"
    field: comment* identifier field_id ":" param+ ";"
    field_id: "@" number
    param: identifier "("? param_argument* ")"? "|"?
    param_argument: value ","?

    enum: comment* "enum" identifier "{" enum_field* "}" ";"
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
    start: preamble (broadcast | device | imports | log)*

    preamble: "version" ":" string

    broadcast: comment* "broadcast" identifier "{" (field | signal)* "}" ";"
    field: identifier ":" (value) ";"
    value : integer | float | string | identifier
    signal: "signal" identifier "{" field* "}" ";"

    log : comment* "log" identifier ":" param+ ";"
    command : comment* "command" identifier ":" param+ "{"? (cmd_arg | cmd_ret)* "}"? ";"
    cmd_arg: comment* "arg" identifier "@" integer ":" param+ ";"
    cmd_ret: comment* "ret" identifier "@" integer ":" param+ ";"
    config : comment* "config" identifier ":" param+ ";"

    param: identifier param_args?  "|"?
    param_args : "(" param_argument+ ")"
    param_argument: value ","?

    integer: SIGNED_INT
    float: SIGNED_NUMBER
    string: ESCAPED_STRING

    device : "device" identifier ":" param+ "{" (command | config)* "}" ";"

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


def convert_params(params: dict[str, Callable]) -> dict[str, Any]:
    convertion_table = {
        "range": lambda x: {"min_value": x[0], "max_value": x[1]},
        "scale": lambda x: {"scale": x[0], "offset": x[1]},
        "mux": lambda x: {"mux": x[0], "mux_count": x[1]},
        "unit": lambda x: {"unit": x[0]},
        "endianess": lambda x: {"byte_order": x[0]},
    }

    values: dict[str, Callable] = {}
    for name, value in params.items():
<<<<<<< HEAD
<<<<<<< HEAD
        values.update(convertion_table[name](value))
=======
        values = values | convertion_table[name](value)  # type: ignore
>>>>>>> a3dc73d (Passing strict mypy rules and fixed tests for new serde)
=======
        values.update(convertion_table[name](value))  # type: ignore
>>>>>>> 925c042 (backup)

    return values


class FcpV2Transformer(Transformer):
    def __init__(self, filename: str) -> None:
        self.filename = pathlib.Path(filename)
        self.path = self.filename.parent

        with open(self.filename) as f:
            self.source = f.read()

        self.error_logger = ErrorLogger({self.filename.name: self.source})

    def preamble(self, args: list[str]) -> Union[Ok, Error]:
        if args[0] == "3":
            return Ok(None)
        else:
            return Error("Expected IDL version 3")

    def dot(self, args: list[str]) -> str:
        return "."

    def underscore(self, args: list[str]) -> str:
        return "_"

    def identifier(self, args: list[str]) -> str:
        return args[0]

    def import_identifier(self, args: list[str]) -> str:
        identifier = "".join([arg for arg in args])
        return identifier

    def param(self, args: list[str]) -> Tuple[str, ...]:
        return tuple(args)

    def param_argument(self, args: list[str]) -> str:
        return args[0]

    def field_id(self, args: list[str]) -> str:
        return args[0]

    @v_args(tree=True)
    def field(self, tree: ParseTree) -> Union[Ok, Error]:
        if isinstance(tree.children[0], Comment):
            comment, name, field_id, *values = tree.children
            comment = Comment(comment.value)  # type: ignore
            name = name.value if name else ""  # type: ignore
        else:
            name, field_id, *values = tree.children
            comment = Comment("")  # type: ignore

        type = values[0][0]  # type: ignore

        params = {name.value: value for name, *value in values[1:]}  # type: ignore
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

    @v_args(tree=True)
    def struct(self, tree: ParseTree) -> Union[Ok, Error]:
        if isinstance(tree.children[0], Comment):
            comment, name, *fields = tree.children
        else:
            name, *fields = tree.children
            comment = Comment("")  # type: ignore

        meta = get_meta(tree, self)  # type: ignore
        return Ok(
            struct.Struct(
                name=name.value,  # type: ignore
                signals=[x.Q() for x in fields],  # type: ignore
                meta=meta,
                comment=comment,  # type: ignore
            )
        )

    @v_args(tree=True)
    def enum_field(self, tree: ParseTree) -> Union[Ok, Error]:
        name, value = tree.children

        meta = get_meta(tree, self)  # type: ignore
        return Ok(enum.Enumeration(name=name, value=value, meta=meta))  # type: ignore

    @v_args(tree=True)
    def enum(self, tree: ParseTree) -> Union[Ok, Error]:
        args = tree.children

        if isinstance(args[0], Comment):
            comment, name, *fields = args
        else:
            name, *fields = args
            comment = Comment("")  # type: ignore

        fields = [field.Q() for field in fields]  # type: ignore

        meta = get_meta(tree, self)  # type: ignore
        return Ok(enum.Enum(name=name, enumeration=fields, meta=meta, comment=comment))  # type: ignore

    @result_shortcut
    def imports(self, args: list[str]) -> Union[Ok, Error]:
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

    def value(self, args: list[str]) -> str:
        return args[0]

    def number(self, args: list[str]) -> int | float:
        try:
            return int(args[0].value)  # type: ignore
        except ValueError:
            return float(args[0].value)  # type: ignore

    def string(self, args: list[str]) -> str:
        return args[0].value[1:-1]  # type: ignore

    def comment(self, args: list[str]) -> Comment:
        return Comment(args[0].value.replace("/*", "").replace("*/", ""))  # type: ignore

    def start(self, args: list[str]) -> Ok:
        args = [arg.Q() for arg in args if arg.Q() is not None]  # type: ignore

        imports = list(filter(lambda x: isinstance(x, Module), args))
        not_imports = list(filter(lambda x: not isinstance(x, Module), args))
        return Ok(Module(self.filename.name, not_imports, self.source, imports))  # type: ignore


class FpiTransformer(Transformer):
    def __init__(self, filename: str) -> None:
        self.filename = pathlib.Path(filename)
        self.path = self.filename.parent

        with open(self.filename) as f:
            self.source = f.read()

        self.error_logger = ErrorLogger({self.filename: self.source})  # type: ignore

    def preamble(self, args: list[str]) -> Union[Ok, Error]:
        if args[0] == "3":
            return Ok(None)
        else:
            return Error(
                self.error_logger.error(
                    f"Expected IDL version 3 [{self.filename.name}]"
                )
            )

    def identifier(self, args: list[str]) -> str:
        return args[0].value  # type: ignore

    def value(self, args: list[str]) -> str:
        return args[0]

    def float(self, args: list[str]) -> float:
        return float(args[0].value)  # type: ignore

    def integer(self, args: list[str]) -> int:
        return int(args[0].value)  # type: ignore

    def string(self, args: list) -> Any:
        return args[0].value[1:-1]

    def param(self, args: list[str]) -> tuple[str, ...]:
        return tuple(args)

    def param_args(self, args: list[str]) -> str:
        return args[0]

    def param_argument(self, args: list[str]) -> str:
        return args[0]

    @v_args(tree=True)
    def field(self, tree: ParseTree) -> tuple[Any, ...]:
        name, value = tree.children
        return (name, value)

    @v_args(tree=True)
    def signal(self, tree: ParseTree) -> broadcast.BroadcastSignal:
        name, *fields = tree.children
        fields = {name: value for name, value in fields}  # type: ignore
        meta = get_meta(tree, self)  # type: ignore
        return broadcast.BroadcastSignal(name, fields, meta=meta)  # type: ignore

    @v_args(tree=True)
    def broadcast(self, tree: ParseTree) -> Union[Ok, Error]:
        if isinstance(tree.children[0], Comment):
            comment, name, *fields = tree.children
        else:
            name, *fields = tree.children
            comment = Comment("")  # type: ignore

        signals = filter(lambda x: isinstance(x, broadcast.BroadcastSignal), fields)
        fields = list(
            filter(lambda x: not isinstance(x, broadcast.BroadcastSignal), fields)
        )

        field_names = [field[0] for field in fields]  # type: ignore
        if len(field_names) != len(set(field_names)):
            return Error(self.error_logger.error(f"Duplicated key in broadcast {name}"))

        meta = get_meta(tree, self)  # type: ignore
        return Ok(
            broadcast.Broadcast(
                name=name,  # type: ignore
                field={name: value for name, value in fields},  # type: ignore
                signals=signals,  # type: ignore
                meta=meta,
                comment=comment,  # type: ignore
            )
        )

    def comment(self, args: list[str]) -> Comment:
        return Comment(args[0].value.replace("/*", "").replace("*/", ""))  # type: ignore

    def imports(self, args: list[str]) -> Union[Ok, Error]:
        filename = self.path / (args[0] + ".fpi")
        try:
            with open(filename) as f:
                module = (
                    FpiTransformer(filename).transform(fpi_parser.parse(f.read())).Q()  # type: ignore
                )
                module.filename = filename.name
        except Exception as e:
            # logging.error(e)
            traceback.print_exc()
            return Error(self.error_logger.error(f"Could not import {filename}\n{e}"))

        return Ok(module)

    @v_args(tree=True)
    def device(self, tree: ParseTree) -> Union[Ok, Error]:
        name, *children = tree.children

        fields = filter(lambda x: not isinstance(x, Ok), children)
        fields = {name: value for name, value in fields}  # type: ignore

        children = filter(lambda x: isinstance(x, Ok), children)  # type: ignore
        children = [child.unwrap() for child in children]  # type: ignore

        commands = filter(lambda x: isinstance(x, cmd.Command), children)
        configs = filter(lambda x: isinstance(x, config.Config), children)

        meta = get_meta(tree, self)  # type: ignore
        return Ok(
            device.Device(
                name=name,  # type: ignore
                id=fields["id"],  # type: ignore
                commands=commands,  # type: ignore
                configs=configs,  # type: ignore
                meta=meta,
            )
        )

    @v_args(tree=True)
    def log(self, tree: ParseTree) -> Union[Ok, Error]:
        if isinstance(tree.children[0], Comment):
            comment, name, *fields = tree.children
        else:
            name, *fields = tree.children
            comment = Comment("")  # type: ignore

        meta = get_meta(tree, self)  # type: ignore
        fields = {name: value for name, value in fields}  # type: ignore

        n_args = fields.get("n_args") or 0  # type: ignore
        return Ok(
            log.Log(
                id=fields["id"],  # type: ignore
                name=name,  # type: ignore
                comment=comment,  # type: ignore
                string=fields["str"],  # type: ignore
                n_args=n_args,
                meta=meta,
            )
        )

    @v_args(tree=True)
    def config(self, tree: ParseTree) -> Union[Ok, Error]:
        if isinstance(tree.children[0], Comment):
            comment, name, *fields = tree.children
        else:
            name, *fields = tree.children
            comment = Comment("")  # type: ignore

        type = fields[0][0]  # type: ignore
        fields = {name: value for name, value in fields[1:]}  # type: ignore
        meta = get_meta(tree, self)  # type: ignore
        return Ok(
            config.Config(
                name,  # type: ignore
                fields["id"],  # type: ignore
                type,
                fields["device"],  # type: ignore
                comment=comment,  # type: ignore
                meta=meta,
            )
        )

    @v_args(tree=True)
    def command(self, tree: ParseTree) -> Union[Ok, Error]:
        if isinstance(tree.children[0], Comment):
            comment, name, *fields = tree.children
        else:
            name, *fields = tree.children
            comment = Comment("")  # type: ignore

        args = [field for field in fields if isinstance(field, cmd.CommandArg)]
        rets = [field for field in fields if isinstance(field, cmd.CommandRet)]
        fields = [field for field in fields if isinstance(field, tuple)]

        fields = {name: value for name, value in fields}  # type: ignore
        meta = get_meta(tree, self)  # type: ignore
        return Ok(
            cmd.Command(
                name,  # type: ignore
                fields["id"],  # type: ignore
                args,  # type: ignore
                rets,  # type: ignore
                fields.get("device"),  # type: ignore
                comment=comment,  # type: ignore
                meta=meta,
            )
        )

    @v_args(tree=True)
    def cmd_arg(self, tree: ParseTree) -> cmd.CommandArg:
        if isinstance(tree.children[0], Comment):
            comment, name, id, *params = tree.children
        else:
            name, id, *params = tree.children
            # comment = Comment("")

        type, *params = params
        return cmd.CommandArg(name=name, type=type[0], id=id)  # type: ignore

    @v_args(tree=True)
    def cmd_ret(self, tree: ParseTree) -> cmd.CommandRet:
        if isinstance(tree.children[0], Comment):
            comment, name, id, *params = tree.children
        else:
            name, id, *params = tree.children
            # comment = Comment("")

        type, *params = params
        return cmd.CommandRet(name=name, type=type[0], id=id)  # type: ignore

    @result_shortcut
    def start(self, args: list[str]) -> Union[Ok, Error]:
        args = [arg.Q() for arg in args if arg.Q() is not None]  # type: ignore

        imports = list(filter(lambda x: isinstance(x, Module), args))
        not_imports = list(filter(lambda x: not isinstance(x, Module), args))

        return Ok(Module(self.filename.name, not_imports, self.source, imports))  # type: ignore


def resolve_imports(module: dict[str, Any]) -> Union[Ok, Error]:
    def merge(module1: dict, module2: dict) -> dict:
        merged = {}
        keys = list(module1.keys()) + list(module2.keys())
        for key in keys:
            merged[key] = (module1.get(key) or []) + (module2.get(key) or [])

        return merged

    nodes: dict[str, list[Any]] = {
        "enum": [],
        "struct": [],
        "broadcast": [],
        "device": [],
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


def deduplicate(module: dict[str, Any]) -> Ok:
    return Ok(
        {
            type: {node.get_name(): node for node in module[type]}
            for type in module.keys()
        }
    )


def merge(fcp: dict[str, Any], fpi: dict[str, Any]) -> Ok:
    fcp = {key: fcp[key] for key in fcp.keys() & {"struct", "enum"}}
    fpi = {key: fpi[key] for key in fpi.keys() & {"device", "broadcast", "log"}}
    fcp.update(fpi)
    return Ok(fcp)


def convert(module: dict[str, Any]) -> Ok:
    to_list = lambda t, v: [from_dict(t, x) for x in v]

    a = v2.FcpV2(
        broadcasts=to_list(broadcast.Broadcast, module["broadcast"].values()),
        devices=to_list(device.Device, module["device"].values()),
        structs=to_list(struct.Struct, module["struct"].values()),
        enums=to_list(enum.Enum, module["enum"].values()),
        logs=to_list(log.Log, module["log"].values()),
        version="3.0",
    )

    return Ok(
        v2.FcpV2(
            broadcasts=to_list(broadcast.Broadcast, module["broadcast"].values()),
            devices=to_list(device.Device, module["device"].values()),
            structs=to_list(struct.Struct, module["struct"].values()),
            enums=to_list(enum.Enum, module["enum"].values()),
            logs=to_list(log.Log, module["log"].values()),
            version="3.0",
        )
    )


@result_shortcut
def get_sources(module: Any) -> dict[str, str]:
    sources = {module.filename: module.source}
    for mod in module.imports:
        sources.update(get_sources(mod))

    return sources


@result_shortcut
def get_fcp(fcp: str, fpi: str) -> Union[Ok, Error]:
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
                    e._format_expected(e.allowed),  #
                )
            )

    fcp = FcpV2Transformer(fcp_filename).transform(fcp_ast).Q()
    fcp_sources = get_sources(fcp)
    fcp = deduplicate(resolve_imports(fcp).Q()).Q()  # type: ignore

    fpi_filename = fpi
    with open(fpi_filename) as f:
        fpi_ast = fpi_parser.parse(f.read())

    fpi = FpiTransformer(fpi_filename).transform(fpi_ast).Q()
    fpi_sources = get_sources(fpi)
    fpi = deduplicate(resolve_imports(fpi).Q()).Q()  # type: ignore

<<<<<<< HEAD
    fcp_sources.update(fpi_sources)
<<<<<<< HEAD
    return Ok((convert(merge(fcp, fpi).Q()), fcp_sources))
=======
    return Ok((convert(merge(fcp, fpi).Q()), fcp_sources | fpi_sources))  # type: ignore
>>>>>>> c2a9dcd (Typing for passing mypy tests)
=======
    return Ok((convert(merge(fcp, fpi).Q()), fcp_sources))  # type: ignore
>>>>>>> 925c042 (backup)
