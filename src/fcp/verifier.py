from beartype.typing import Callable, NoReturn, Dict
from .result import Ok, Result
from .maybe import catch
from .error import FcpError
from .types import Nil
from .specs.v2 import FcpV2


class Verifier:
    def __init__(self) -> None:
        self.checks: Dict[str, Callable] = {}

    def register(self, category: str, function: Callable) -> NoReturn:
        if category not in self.checks.keys():
            self.checks[category] = []
        self.checks[category].append(function)

    @catch
    def run_checks(self, category: str, fcp: FcpV2) -> Result[Nil, FcpError]:
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


def register(verifier: Verifier, category: str) -> Callable:
    def decorator(f: Callable) -> Callable:
        verifier.register(category, f)
        return f

    return decorator


class GeneralVerifier(Verifier):
    def __init__(self) -> None:
        super().__init__()
