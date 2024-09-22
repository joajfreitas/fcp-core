import logging
from functools import reduce
from collections import Counter
from typing import Any, Tuple, Generator, Callable, Union

from .result import Ok, Error, Result
from .colors import Color
from .error_logger import ErrorLog


def simple_error(f: Callable) -> Callable:  # type: ignore
    # @functools.wraps(f)
    def wrapper(obj: Any, *args: Any) -> Union[Ok, Error]:
        cond, error = f(obj, *args)
        if not cond:
            return Ok(())
        else:
            return Error(obj.error_logger.log_node(args[0], error))

    return wrapper


class ErrorLogger:
    def __init__(self, sources: dict[str, str]) -> None:
        self.sources = sources

    def add_source(self, name: str, source: str) -> None:
        self.sources[name] = source

    def highlight(
        self, source: str, prefix_with_line: str, prefix_without_line: str
    ) -> str:
        ss = ""
        for i, line in enumerate(source.split("\n")):
            prefix = prefix_with_line if i == 0 else prefix_without_line
            ss += prefix + line + "\n"
            line = line.replace("\t", "    ")
            ss += prefix_without_line + Color.boldred("~" * len(line)) + "\n"

        return ss

    def log_location(
        self, error: str, filename: str, line: int, column: int, source: str
    ) -> str:
        line_len = len(str(line))

        prefix_with_line = Color.boldblue(f"{line} | ")
        prefix_without_line = Color.boldblue(" " * line_len + " | ")

        ss = (
            ""
            if error == ""
            else Color.boldred("error: ") + Color.boldwhite(error) + "\n"
        )
        ss += (
            " " * line_len
            + Color.boldblue("---> ")
            + f"{filename}:{line}:{column}"
            + "\n"
        )
        ss += prefix_without_line + "\n"

        ss += self.highlight(source, prefix_with_line, prefix_without_line)

        return ss

    def log_node(self, node: Any, error: str = "") -> str:
        source = self.sources[node.meta.filename]
        return self.log_location(
            error,
            node.meta.filename,
            node.meta.line,
            node.meta.column,
            source[node.meta.start_pos : node.meta.end_pos],
        )

    def log_duplicates(self, error: str, duplicates: list[Any]) -> str:
        return (
            Color.boldblue("error: ")
            + Color.boldwhite(error)
            + "\n"
            + "\n".join(map(lambda x: self.log_node(x), duplicates))
        )

    def log_lark_unexpected_characters(self, filename, exception):
        return (
            ErrorLog()
            .with_line(Color.boldwhite(f"Unexpected character '{exception.char}'"))
            .with_line(" -> ")
            .with_location(filename, exception.line, exception.column)
            .with_newline(ammount=2)
            .with_line("Expected one of:")
            .with_newline()
            .with_list(exception.allowed, transform=lambda x: "* " + x)
            .with_newline(ammount=2)
            .with_surrounding(
                self.sources[filename], exception.line - 1, exception.column - 1
            )
            .error()
        )

    def error(self, error: str) -> str:
        return Color.boldred("Error: ") + Color.boldwhite(error)


class BaseVerifier:
    """Base class for verifiers"""

    def __init__(self, sources: dict[str, str]) -> None:
        self.error_logger = ErrorLogger(sources)

    def apply_check(self, category: str, value: Any) -> Union[Ok, Error, Result]:
        result = Ok(())
        for name, f in self.__class__.__dict__.items():
            if name.startswith(f"check_{category}"):
                if isinstance(value, tuple):
                    result = result.compound(f(self, *value))
                else:
                    result = result.compound(f(self, value))

        return result

    def apply_checks(self, category: str, values: Any) -> Union[Ok, Error]:
        results = list(map(lambda value: self.apply_check(category, value), values))
        return reduce(lambda x, y: x.compound(y), results, Ok(()))

    def verify(self, fcp_v2: Any) -> Union[Ok, Error]:
        logging.debug("Running verifier")

        result = Ok(())

        result = result.compound(self.apply_check("fcp_v2", fcp_v2))
        result = result.compound(
            self.apply_checks("enum", map(lambda x: (x,), fcp_v2.enums))
        )
        result = result.compound(
            self.apply_checks("struct", map(lambda x: (x,), fcp_v2.structs))
        )

        return result


class Verifier(BaseVerifier):
    def __init__(self, sources: dict[str, str]) -> None:
        self.error_logger = ErrorLogger(sources)

    def check_fcp_v2_duplicate_typenames(self, fcp_v2: Any) -> Union[Ok, Error]:
        def naming(x: Any) -> Any:
            return x.name

        duplicates = list(
            Verifier.get_duplicates(fcp_v2.structs + fcp_v2.enums, naming, naming)
        )

        if len(duplicates) == 0:
            return Ok(())
        else:
            return Error(
                self.error_logger.log_duplicates(
                    "Found duplicate typenames in fcp configuration", duplicates
                )
            )

    def check_struct_duplicate_signals(self, struct: Any) -> Union[Ok, Error]:
        def naming(x: Any) -> Any:
            return x.name

        duplicates = list(Verifier.get_duplicates(struct.signals, naming, naming))
        if len(duplicates) == 0:
            return Ok(())
        else:
            return Error(
                self.error_logger.log_duplicates(
                    f"Found duplicate signals in struct {struct.name}",
                    duplicates,
                )
            )

    # def check_signal_type(self, signal: Any) -> Union[Ok, Error]:
    #    types = [
    #        signess + str(width) for signess in ["i", "u"] for width in range(1, 65)
    #    ]
    #    types += ["f32", "f64"]

    #    if signal.type in types:
    #        return Ok(())
    #    else:
    #        return Error(self.error_logger.log_node(signal, "Invalid signal type"))

    @simple_error
    def check_signal_name_is_identifier(self, signal: Any) -> Tuple[bool, str]:
        return (
            not signal.name.isidentifier(),
            f"{signal.name} is not a valid identifier",
        )

    def check_enum_duplicated_values(self, enum: Any) -> Union[Ok, Error]:
        duplicates = list(
            Verifier.get_duplicates(
                enum.enumeration, lambda x: x.value, lambda x: x.name
            )
        )
        if len(duplicates) == 0:
            return Ok(())
        else:
            return Error(f"Found duplicate values in enum {enum.name}: {duplicates}")

    @simple_error
    def check_enum_name_is_identifier(self, enum: Any) -> Tuple[bool, str]:
        return not enum.name.isidentifier(), f"{enum.name} is not a valid identifier"

    @simple_error
    def check_broadcast_name_is_identifier(self, broadcast: Any) -> Tuple[bool, str]:
        return (
            not broadcast.name.isidentifier(),
            f"{broadcast.name} is not a valid identifier",
        )

    @simple_error
    def check_device_name_is_identifier(self, device: Any) -> Tuple[bool, str]:
        return (
            not device.name.isidentifier(),
            f"{device.name} is not a valid identifier",
        )

    @staticmethod
    def get_duplicates(
        container: Any, selector: Any, naming: Any
    ) -> Generator[Any, None, None]:
        selection = list(map(selector, container))

        count = Counter(selection)
        duplicates = list(filter(lambda x: x[1] > 1, count.items()))

        for duplicate in duplicates:
            for node, value in zip(container, selection):
                if value == duplicate[0]:
                    yield node
