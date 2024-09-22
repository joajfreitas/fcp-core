from typing import TypeVar, Callable

from .colors import Color


def highlight(source: str, prefix_with_line: str, prefix_without_line: str) -> str:
    ss = ""
    for i, line in enumerate(source.split("\n")):
        prefix = prefix_with_line if i == 0 else prefix_without_line
        ss += prefix + line + "\n"
        line = line.replace("\t", "    ")
        ss += prefix_without_line + Color.boldred("~" * len(line)) + "\n"

    return ss


class ErrorLog:
    Self = TypeVar("Self", bound="ErrorLog")

    def __init__(self) -> None:
        self.buffer = Color.boldred("Error: ")

    def with_newline(self: Self, amount: int = 1) -> Self:
        self.buffer += amount * "\n"
        return self

    def with_list(
        self: Self, list: list[str], transform: Callable[[str], str] = lambda x: x
    ) -> Self:
        self.buffer += "\n".join(["\t" + transform(x) for x in list])
        return self

    def with_line(self: Self, line: str) -> Self:
        self.buffer += line
        return self

    def with_location(self: Self, filename: str, line: int, column: int) -> Self:
        self.buffer += f"{filename}:{line}:{column}"

        return self

    def with_surrounding(self: Self, source: str, line: int, column: int) -> Self:
        lines = source.split("\n")
        starting_line = line - 2 if line > 0 else 0
        ending_line = line + 1 if line < len(lines) else len(lines)

        prefix_with_line = Color.boldblue(f"{starting_line+1} | ")
        prefix_without_line = Color.boldblue(" " * len(str(line)) + " | ")

        source = "\n".join(lines[starting_line:ending_line])

        ss = highlight(source, prefix_with_line, prefix_without_line)

        self.buffer += ss

        return self

    def error(self) -> str:
        return self.buffer
