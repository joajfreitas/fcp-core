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

from beartype.typing import List, Dict, Any, Tuple
from lark import UnexpectedCharacters
from pathlib import Path

from .colors import Color
from .error import FcpError


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
            ss += prefix + " " + line + "\n"
            line = line.replace("\t", "    ")
            ss += prefix_without_line + " " + Color.boldred("~" * len(line)) + "\n"

        return ss

    def log_location(self, line: int, source: str) -> str:
        """Log source code location."""
        line_len = len(str(line))

        prefix_with_line = Color.boldblue(f"{line} |")
        prefix_without_line = Color.boldblue(" " * line_len + " |")

        ss = prefix_without_line + "\n"
        ss += self._highlight(source, prefix_with_line, prefix_without_line)

        return ss

    def log_node(self, node: Any) -> str:
        """Log fcp node."""
        source = self.sources[Path(node.meta.filename).name]
        lines = source.split("\n")
        return self.log_location(
            node.meta.line,
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

    def log_lark_unexpected_characters(self, exception: UnexpectedCharacters) -> str:
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

        def format_msg(
            msg: Tuple[str, Any, Tuple[str, int]], prefix: str, arrow: str
        ) -> str:
            msg, node, (source_file, line_number) = msg
            if self.enable_file_paths:
                if node is not None:
                    node_position = (
                        f"\n   ↳ [{Path(node.meta.filename).name}:{node.meta.line}]"
                    )
                else:
                    node_position = ""

                return (
                    f"{arrow} {prefix}{msg}"
                    + "\n"
                    + f"   ↳ [{source_file.name}:{line_number}]"
                    + node_position
                )
            else:
                return f"{arrow} {prefix}{msg}"

        ss = ""

        for i, (msg, node, (source_file, line_number)) in enumerate(error.msg):
            if i == 0:
                prefix = Color.boldred("Error:") + " "
                arrow = "  →"
            else:
                prefix = ""
                arrow = "  ↳"
            ss += (
                format_msg((msg, node, (source_file, line_number)), prefix, arrow)
                + "\n"
            )
            if node is not None:
                ss += self.log_node(node)
        return ss
