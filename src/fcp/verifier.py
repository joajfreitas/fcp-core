from beartype.typing import Callable, NoReturn, Dict, Optional, Any, Tuple
from .result import Ok, Result, Err
from .maybe import catch
from .error import FcpError
from .types import Nil
from .specs.v2 import FcpV2
from .specs.impl import Impl
from .specs.struct_field import StructField
from .specs.struct import Struct
from .specs.enum import Enum


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
        self.run_checks("field", fcp).attempt()
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

        impls = [(impl.name, impl.protocol) for impl in fcp.impls]
        if impls.count((left.name, left.protocol)) > 1:
            return Err(FcpError("Duplicate impls", node=left))
        else:
            return Ok(())

    @register(general_verifier, "field")  # type: ignore
    def check_duplicate_struct_fields(
        self: Any, fcp: FcpV2, left: Tuple[Struct, StructField]
    ) -> Result[Nil, FcpError]:

        print(left)
        struct, left_signal = left

        signal_names = [field.name for field in struct.fields]
        print(left_signal)
        if signal_names.count(left_signal.name) > 1:
            return Err(FcpError("Duplicate fields", node=left_signal))
        else:
            return Ok(())

    @register(general_verifier, "struct")  # type: ignore
    def check_struct_contains_struct_fields(
        self: Any, fcp: FcpV2, struct: Struct
    ) -> Result[Nil, FcpError]:
        if len(struct.fields) == 0:
            return Err(FcpError("Struct has no signal", node=struct))
        else:
            return Ok(())

    @register(general_verifier, "enum")  # type: ignore
    def check_enum_duplicate_enumerations_names(
        self: Any, fcp: FcpV2, enum: Enum
    ) -> Result[Nil, FcpError]:

        enumeration_names = [enumeration.name for enumeration in enum.enumeration]
        for enumeration in enum.enumeration:
            if enumeration_names.count(enumeration.name) > 1:
                return Err(FcpError("Duplicated enumration name", node=enumeration))

        return Ok(())

    @register(general_verifier, "enum")  # type: ignore
    def check_enum_duplicate_enumerations_values(
        self: Any, fcp: FcpV2, enum: Enum
    ) -> Result[Nil, FcpError]:

        enumeration_names = [enumeration.value for enumeration in enum.enumeration]
        for enumeration in enum.enumeration:
            if enumeration_names.count(enumeration.value) > 1:
                return Err(FcpError("Duplicated enumration name", node=enumeration))

        return Ok(())

    return general_verifier
