from beartype.typing import Callable, NoReturn, Dict, Optional, Any
from .result import Ok, Result, Err
from .maybe import catch
from .error import FcpError
from .types import Nil
from .specs.v2 import FcpV2
from .specs.impl import Impl


class Verifier:
    def __init__(self) -> None:
        self.checks: Dict[str, Callable] = {"uncategorized": []}

    def register(self, function: Callable, category: Optional[str] = None) -> NoReturn:
        if category is None:
            self.checks["uncategorized"].append(function)
            return

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
        self.run_checks("impl", fcp).attempt()
        self.run_checks("signal_block", fcp).attempt()
        self.run_checks("type", fcp).attempt()
        self.run_checks("uncategorized", fcp).attempt()

        return Ok(())


def register(verifier: Verifier, category: Optional[str] = None) -> Callable:
    def decorator(f: Callable) -> Callable:
        verifier.register(f, category)
        return f

    return decorator


class GeneralVerifier(Verifier):
    def __init__(self) -> None:
        super().__init__()


def make_general_verifier() -> GeneralVerifier:
    general_verifier = GeneralVerifier()

    @register(general_verifier, "type")  # type: ignore
    def check_duplicate_typenames(
        self: Any, fcp: FcpV2, type: Any
    ) -> Result[Nil, FcpError]:
        type_names = [type.name for type in fcp.get_types()]

        if type_names.count(type.name) > 1:
            return Err(FcpError("Duplicate type names", node=type))
        else:
            return Ok(())

    @register(general_verifier, "impl")  # type: ignore
    def check_duplicate_impl(
        self: Any, fcp: FcpV2, left: Impl
    ) -> Result[Nil, FcpError]:

        for right in fcp.impls:
            if left.name == right.name and left.protocol == right.protocol:
                return Err(FcpError("Duplicate impls", node=left))

        return Ok(())

    return general_verifier
