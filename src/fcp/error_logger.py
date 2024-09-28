from beartype.typing import Callable, List, Dict, Any
from lark import UnexpectedCharacters

from typing_extensions import Self

from .colors import Color
from .error import FcpError, Level


def highlight(source: str, prefix_with_line: str, prefix_without_line: str) -> str:
    ss = ""
    for i, line in enumerate(source.split("\n")):
        prefix = prefix_with_line if i == 0 else prefix_without_line
        ss += prefix + line + "\n"
        line = line.replace("\t", "    ")
        ss += prefix_without_line + Color.boldred("~" * len(line)) + "\n"

    return ss


class ErrorLog:
    def __init__(self) -> None:
        self.buffer = Color.boldred("Error: ")

    def with_newline(self, amount: int = 1) -> Self:
        self.buffer += amount * "\n"
        return self

    def with_list(
        self, list: List[str], transform: Callable[[str], str] = lambda x: x
    ) -> Self:
        self.buffer += "\n".join(["\t" + transform(x) for x in list])
        return self

    def with_line(self, line: str) -> Self:
        self.buffer += line
        return self

    def with_location(self, filename: str, line: int, column: int) -> Self:
        self.buffer += f"{filename}:{line}:{column}"

        return self

    def with_surrounding(self, source: str, line: int, column: int) -> Self:
        lines = source.split("\n")
        starting_line = line - 2 if line > 0 else 0
        ending_line = line + 1 if line < len(lines) else len(lines)

        prefix_with_line = Color.boldblue(f"{starting_line+1} | ")
        prefix_without_line = Color.boldblue(" " * len(str(line)) + " | ")

        source = "\n".join(lines[starting_line:ending_line])

        ss = highlight(source, prefix_with_line, prefix_without_line)

        self.buffer += ss

        return self

    def with_log_level(self, level: Level) -> Self:
        if level == Level.Error:
            self.buffer += Color.red("Error: ")
        elif level == Level.Warn:
            self.buffer += Color.yellow("Warning: ")
        elif level == Level.Info:
            self.buffer += Color.blue("Info: ")

        return self

    def error(self) -> str:
        return self.buffer


class ErrorLogger:
    def __init__(self, sources: Dict[str, str]) -> None:
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

    def log_duplicates(self, error: str, duplicates: List[Any]) -> str:
        return (
            Color.boldblue("error: ")
            + Color.boldwhite(error)
            + "\n"
            + "\n".join(map(lambda x: self.log_node(x), duplicates))
        )

    def log_lark_unexpected_characters(
        self, filename: str, exception: UnexpectedCharacters
    ) -> str:
        return (
            ErrorLog()
            .with_line(Color.boldwhite(f"Unexpected character '{exception.char}'"))
            .with_line(" -> ")
            .with_location(filename, exception.line, exception.column)
            .with_newline(amount=2)
            .with_line("Expected one of:")
            .with_newline()
            .with_list(exception.allowed, transform=lambda x: "* " + x)
            .with_newline(amount=2)
            .with_surrounding(
                self.sources[filename], exception.line - 1, exception.column - 1
            )
            .error()
        )

    def log_fcp_error(self, fcp_error: FcpError) -> str:
        meta = fcp_error.node.meta
        return (
            ErrorLog()
            .with_log_level(fcp_error.level)
            .with_line(fcp_error.msg)
            .with_newline()
            .with_surrounding(
                self.sources[meta.filename],
                meta.line,
                meta.column,
            )
            .error()
        )

    def error(self, error: str) -> str:
        return Color.boldred("Error: ") + Color.boldwhite(error)
