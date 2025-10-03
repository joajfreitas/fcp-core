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

"""Error."""

from beartype.typing import Dict, Any, Tuple
from typing_extensions import Self
from lark import UnexpectedInput, UnexpectedCharacters, UnexpectedEOF
from pathlib import Path
from inspect import getframeinfo, stack

from .colors import Color
from .result import Err


class FcpError:
    """Fcp error."""

    def __init__(self, msg: str, node: Any = None):
        caller = getframeinfo(stack()[1][0])
        self.msg = [(msg, node, (Path(caller.filename), caller.lineno))]

    def results_in(self, msg: str, node: Any = None) -> Self:
        """Appends error message to the current error."""
        caller = getframeinfo(stack()[1][0])
        self.msg.append((msg, node, (Path(caller.filename), caller.lineno)))
        return self

    def __repr__(self) -> str:
        return "\n".join([msg for msg, _, _ in self.msg])


def error(msg: str, node: Any = None) -> Err[FcpError]:
    """Create an error."""
    return Err(FcpError(msg, node))


class Logger:
    """Logger for errors."""

    def __init__(self, sources: Dict[str, str], enable_file_paths: bool = True) -> None:
        self.sources = sources
        self.enable_file_paths = enable_file_paths

    def add_source(self, name: str, source: str) -> None:
        """Register source files."""
        self.sources[name] = source

    def log_location(self, source: str, line: int) -> str:
        """Log source code location."""
        prefix_with_line = Color.boldblue(f"{line} |")
        prefix_without_line = Color.boldblue(" " * len(str(line)) + " |")

        ss = prefix_without_line + "\n"
        ss += prefix_with_line + " " + source + "\n"
        source = source.replace("\t", "    ")
        return ss + prefix_without_line + " " + Color.boldred("~" * len(source)) + "\n"

    def log_node(self, node: Any) -> str:
        """Log fcp node."""
        lines = self.sources[Path(node.meta.filename).name].split("\n")
        return self.log_location(
            lines[node.meta.line - 1],
            node.meta.line,
        )

    def log_lark_unexpected_characters(self, exception: UnexpectedCharacters) -> str:
        """Log a lark unexpected characters exception."""
        expected_rules = sorted(
            {str(rule.rule.origin.name) for rule in exception.considered_rules}
        )
        return f"Unexpected character '{exception.char}', expected one of: " + str(
            expected_rules
        )

    def log_lark_unexpected_eof(self, exception: UnexpectedEOF) -> str:
        """Log a lark unexpected EOF exception."""
        return "Unexpected EOF"

    def log_lark(self, filename: str, exception: UnexpectedInput) -> str:
        """Log lark errors."""
        if isinstance(exception, UnexpectedCharacters):
            return self.log_lark_unexpected_characters(exception)
        elif isinstance(exception, UnexpectedEOF):
            return self.log_lark_unexpected_eof(exception)
        else:
            return "Unexpected EOF in file " + filename

    def error(self, error: FcpError) -> str:
        """Log an error."""

        def format_msg(
            msg: Tuple[str, Tuple[str, str]], prefix: str, arrow: str
        ) -> str:
            msg, node, (source_file, line_number) = msg

            ss = f"{arrow} {prefix}{msg}"
            if self.enable_file_paths:
                ss += "\n" + f"   ↳ [{source_file.name}:{line_number}]"
                if node is not None:
                    ss += f"\n   ↳ [{Path(node.meta.filename).name}:{node.meta.line}]"

            ss += "\n"

            if node is not None:
                ss += self.log_node(node)
            return ss

        ss = ""

        for i, (msg, node, (source_file, line_number)) in enumerate(error.msg):
            if i == 0:
                prefix = Color.boldred("Error:") + " "
                arrow = "  →"
            else:
                prefix = ""
                arrow = "  ↳"
            ss += format_msg((msg, node, (source_file, line_number)), prefix, arrow)
        return ss
