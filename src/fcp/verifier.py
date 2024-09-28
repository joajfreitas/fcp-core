from beartype.typing import Any, Tuple, Generator, Callable, Dict, List
import logging
from functools import reduce
from collections import Counter

from .result import Ok, Err, Result
from .maybe import catch
from .colors import Color
from .error_logger import ErrorLog
from .error import FcpError
from .types import Nil
from .specs.v2 import FcpV2
from .error_logger import ErrorLogger


def register(verifier, category):
    def decorator(f):
        verifier.register(category, f)
        return f

    return decorator


class Verifier:
    def __init__(self):
        self.checks = {}
        pass

    def register(self, category, function):
        if category not in self.checks.keys():
            self.checks[category] = []
        self.checks[category].append(function)

    @catch
    def run_checks(self, category, fcp):
        for check in self.checks.get(category) or []:
            for node in fcp.get(category).attempt():
                check(fcp, fcp, node).attempt()

        return Ok(())

    @catch
    def verify(self, fcp: FcpV2) -> Result[Nil, FcpError]:
        self.run_checks("struct", fcp).attempt()
        self.run_checks("signal", fcp).attempt()
        self.run_checks("enum", fcp).attempt()
        self.run_checks("extension", fcp).attempt()
        self.run_checks("signal_block", fcp).attempt()

        return Ok(())


class GeneralVerifier(Verifier):
    def __init__(self):
        super().__init__()
