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

"""Error logger."""

from beartype.typing import Callable, List, Dict, Any, Tuple
from lark import UnexpectedCharacters
from pathlib import Path

from typing_extensions import Self

from .colors import Color
from .error import FcpError, Level


def _highlight(source: str, prefix_with_line: str, prefix_without_line: str) -> str:
    """Highligh source code."""
    ss = ""
    for i, line in enumerate(source.split("\n")):
        prefix = prefix_with_line if i == 0 else prefix_without_line
        ss += prefix + line + "\n"
        line = line.replace("\t", "    ")
        ss += prefix_without_line + Color.boldred("~" * len(line)) + "\n"

    return ss


class ErrorLogBuilder:
    """Builder for error logs."""

    def __init__(self, enable_file_paths: bool) -> None:
        self.enable_file_paths = enable_file_paths
        self.buffer = Color.boldred("Error: ")

    def with_newline(self, amount: int = 1) -> Self:
        """Add a new line."""
        self.buffer += amount * "\n"
        return self

    def with_list(
        self, list: List[str], transform: Callable[[str], str] = lambda x: x
    ) -> Self:
        """Add a list."""
        self.buffer += "\n".join(["\t" + transform(x) for x in list])
        return self

    def with_line(self, line: str) -> Self:
        """Add a line."""
        self.buffer += line
        return self

    def with_location(self, filepath: Path, line: int, column: int) -> Self:
        """Add code location."""
        if not self.enable_file_paths:
            filename = filepath.name
        else:
            filename = str(filepath)

        self.buffer += f"{filename}:{line}:{column}"

        return self

    def with_surrounding(self, source: str, line: int, column: int) -> Self:
        """Add source code context."""
        lines = source.split("\n")
        starting_line = line - 2 if line > 0 else 0
        ending_line = line + 1 if line < len(lines) else len(lines)

        prefix_with_line = Color.boldblue(f"{starting_line+1} | ")
        prefix_without_line = Color.boldblue(" " * len(str(line)) + " | ")

        source = "\n".join(lines[starting_line:ending_line])

        ss = _highlight(source, prefix_with_line, prefix_without_line)

        self.buffer += ss

        return self

    def with_log_level(self, level: Level) -> Self:
        """Add a log level marker."""
        if level == Level.Error:
            self.buffer += Color.red("Error: ")
        elif level == Level.Warn:
            self.buffer += Color.yellow("Warning: ")
        elif level == Level.Info:
            self.buffer += Color.blue("Info: ")

        return self

    def error(self) -> str:
        """Build error."""
        return self.buffer


class ErrorLogger:
    """Logger for errors."""

    def __init__(self, sources: Dict[str, str], enable_file_paths: bool = True) -> None:
        self.sources = sources
        self.enable_file_paths = enable_file_paths

    def add_source(self, name: str, source: str) -> None:
        """Register source files."""
        self.sources[name] = source

    def _highlight(
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
        """Log source code location."""
        if not self.enable_file_paths:
            return ""

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

        ss += self._highlight(source, prefix_with_line, prefix_without_line)

        return ss

    def log_node(self, node: Any, error: str = "") -> str:
        """Log fcp node."""
        source = self.sources[Path(node.meta.filename).name]
        lines = source.split("\n")
        return self.log_location(
            error,
            node.meta.filename,
            node.meta.line,
            node.meta.column,
            lines[node.meta.line - 1],
        )

    def log_duplicates(self, error: str, duplicates: List[Any]) -> str:
        """Log duplicated values error."""
        return (
            Color.boldblue("error: ")
            + Color.boldwhite(error)
            + "\n"
            + "\n".join(map(lambda x: self.log_node(x), duplicates))
        )

    def log_lark_unexpected_characters(
        self, filename: str, exception: UnexpectedCharacters
    ) -> str:
        """Log a lark unexpected characters exception."""
        return f"Unexpected character '{exception.char}', expected one of: " + str(
            list(
                set([str(rule.rule.origin.name) for rule in exception.considered_rules])
            )
        )

    def log_lark(self, filename: str, exception: Exception) -> str:
        """Log lark errors."""
        if isinstance(exception, UnexpectedCharacters):
            return self.log_lark_unexpected_characters(filename, exception)
        else:
            return "Unexpected EOF in file " + filename

    def error(self, error: FcpError) -> str:
        """Log an error."""

        def format_msg(msg: Tuple[str, Any, Tuple[str, int]]) -> str:
            msg, _, (source_file, line_number) = msg
            if self.enable_file_paths:
                return f" -> {msg} [{source_file.name}:{line_number}]"
            else:
                return f" -> {msg}"

        ss = ""
        for msg, node, (source_file, line_number) in error.msg:
            ss += format_msg((msg, node, (source_file, line_number))) + "\n"
            if node is not None:
                ss += self.log_node(node)

        return ss
