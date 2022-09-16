import logging
import sys
from functools import reduce
from collections import Counter
from termcolor import colored, cprint
import functools

from .result import Ok, Error


class colors:
    @staticmethod
    def red(s):
        return colored(s, "red")

    @staticmethod
    def yellow(s):
        return colored(s, "yellow")

    @staticmethod
    def orange(s):
        return colored(s, "orange")

    @staticmethod
    def blue(s):
        return colored(s, "blue")

    @staticmethod
    def white(s):
        return colored(s, "white")

    @staticmethod
    def boldred(s):
        return colored(s, "red", attrs=["bold"])

    @staticmethod
    def boldyellow(s):
        return colored(s, "yellow", attrs=["bold"])

    @staticmethod
    def boldorange(s):
        return colored(s, "orange", attrs=["bold"])

    @staticmethod
    def boldblue(s):
        return colored(s, "blue", attrs=["bold"])

    @staticmethod
    def boldwhite(s):
        return colored(s, "white", attrs=["bold"])


def simple_error(f):
    # @functools.wraps(f)
    def wrapper(obj, node):
        cond, error = f(obj, node)
        if not cond:
            return Ok(())
        else:
            return Error(obj.error_logger.log_node(node, error))

    return wrapper


class ErrorLogger:
    def __init__(self, sources):
        self.sources = sources

    def add_source(self, name, source):
        self.sources[name] = source

    def highlight(self, source, prefix_with_line, prefix_without_line):
        ss = ""
        for i, line in enumerate(source.split("\n")):
            prefix = prefix_with_line if i == 0 else prefix_without_line
            ss += prefix + line + "\n"
            line = line.replace("\t", "    ")
            ss += (
                prefix_without_line
                + colored("~" * len(line), "red", attrs=["bold"])
                + "\n"
            )

        return ss

    def log_location(self, error, filename, line, column, source):
        line_len = len(str(line))

        prefix_with_line = colors.boldblue(f"{line} | ")
        prefix_without_line = colors.boldblue(" " * line_len + " | ")

        ss = (
            ""
            if error == ""
            else colors.boldred("error: ") + colors.boldwhite(error) + "\n"
        )
        ss += (
            " " * line_len
            + colors.boldblue(f"---> ")
            + f"{filename}:{line}:{column}"
            + "\n"
        )
        ss += prefix_without_line + "\n"

        ss += self.highlight(source, prefix_with_line, prefix_without_line)

        return ss

    def log_node(self, node, error=""):
        source = self.sources[node.meta.filename]
        return self.log_location(
            error,
            node.meta.filename,
            node.meta.line,
            node.meta.column,
            source[node.meta.start_pos : node.meta.end_pos],
        )

    def log_duplicates(self, error, duplicates):
        return (
            colors.boldblue("error: ")
            + colors.boldwhite(error)
            + "\n"
            + "\n".join(map(lambda x: self.log_node(x), duplicates))
        )

    def log_surrounding(self, error, filename, line, column, tip=""):

        ss = self.error(error) + "\n"
        lines = self.sources[filename].split("\n")
        starting_line = line - 2 if line > 0 else 0
        ending_line = line if line < len(lines) else len(lines)

        prefix_with_line = colors.boldblue(f"{starting_line+1} | ")
        prefix_without_line = colors.boldblue(" " * len(str(line)) + " | ")

        source = "\n".join(lines[starting_line:ending_line])
        print(source)

        ss += self.highlight(source, prefix_with_line, prefix_without_line)

        ss += tip

        return ss

    def error(self, error):
        return colors.boldred("Error: ") + colors.boldwhite(error)


class Verifier:
    def __init__(self, sources):
        self.error_logger = ErrorLogger(sources)
        pass

    def check_fcp_v2_duplicate_typenames(self, fcp_v2):
        naming = lambda x: x.name
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

    def check_fcp_v2_duplicate_broadcasts(self, fcp_v2):
        naming = lambda x: x.name
        duplicates = list(Verifier.get_duplicates(fcp_v2.broadcasts, naming, naming))
        if len(duplicates) == 0:
            return Ok(())
        else:
            return Error(
                self.error_logger.log_duplicates(
                    "Found duplicate broadcasts in fcp configuration",
                    duplicates,
                )
            )

    def check_struct_duplicate_signals(self, struct):
        naming = lambda x: x.name
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

    def check_signal_type(self, signal):
        types = [
            signess + str(width) for signess in ["i", "u"] for width in range(1, 65)
        ]
        types += ["f32", "f64"]

        if signal.type in types:
            return Ok(())
        else:
            return Error(self.error_logger.log_node(signal, "Invalid signal type"))

    @simple_error
    def check_signal_name_is_identifier(self, signal):
        return (
            not signal.name.isidentifier(),
            f"{signal.name} is not a valid identifier",
        )

    def check_enum_duplicated_values(self, enum):
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
    def check_enum_name_is_identifier(self, enum):
        return not enum.name.isidentifier(), f"{enum.name} is not a valid identifier"

    @simple_error
    def check_broadcast_name_is_identifier(self, broadcast):
        return (
            not broadcast.name.isidentifier(),
            f"{broadcast.name} is not a valid identifier",
        )

    @simple_error
    def check_device_name_is_identifier(self, device):
        return (
            not device.name.isidentifier(),
            f"{device.name} is not a valid identifier",
        )

    @staticmethod
    def get_duplicates(container, selector, naming):
        selection = list(map(selector, container))

        count = Counter(selection)
        duplicates = list(filter(lambda x: x[1] > 1, count.items()))

        for duplicate in duplicates:
            for node, value in zip(container, selection):
                if value == duplicate[0]:
                    yield node

    def apply_check(self, category, value):
        result = Ok(())
        for name, f in Verifier.__dict__.items():
            if name.startswith(f"check_{category}"):
                result = result.compound(f(self, value))

        return result

    def apply_checks(self, category, values):
        results = map(lambda value: self.apply_check(category, value), values)
        return reduce(lambda x, y: x.compound(y), results)

    def verify(self, fcp_v2):
        logging.info("Running verifier")

        result = Ok(())

        result = result.compound(self.apply_check("fcp_v2", fcp_v2))
        result = result.compound(self.apply_checks("enum", fcp_v2.enums))
        result = result.compound(self.apply_checks("struct", fcp_v2.structs))
        result = result.compound(self.apply_checks("broadcast", fcp_v2.broadcasts))

        for struct in fcp_v2.structs:
            result = result.compound(self.apply_checks("signal", struct.signals))

        return result
