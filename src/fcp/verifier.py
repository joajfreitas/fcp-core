from beartype.typing import Any, Tuple, Generator, Callable, Dict, List
import logging
from functools import reduce
from collections import Counter

from .result import Ok, Err, Result
from .maybe import catch
from .colors import Color
from .error_logger import ErrorLog
from .error_logger import ErrorLogger


def simple_error(f: Callable) -> Callable:  # type: ignore
    # @functools.wraps(f)
    def wrapper(obj: Any, *args: Any) -> Result:
        cond, error = f(obj, *args)
        if not cond:
            return Ok(())
        else:
            return Err(obj.error_logger.log_node(args[0], error))

    return wrapper









class BaseVerifier:
    """Base class for verifiers"""

    def __init__(self, sources: Dict[str, str]) -> None:
        self.error_logger = ErrorLogger(sources)

    def apply_check(self, category: str, value: Any) -> Result[Any, str]:
        result = Ok(())
        for name, f in self.__class__.__dict__.items():
            if name.startswith(f"check_{category}"):
                if isinstance(value, tuple):
                    result = f(self, *value)
                else:
                    result = f(self, value)

        return result

    def apply_checks(self, category: str, values: Any) -> Result[Any, str]:
        results: List[Result[Any]] = list(
            map(lambda value: self.apply_check(category, value), values)
        )
        result: Result[Any] = reduce(lambda x, y: y, results, Ok(()))

        return result

    def verify(self, fcp_v2: Any) -> Result[Any, str]:
        logging.debug("Running verifier")

        result: Result[Any] = Ok(())

        result = self.apply_check("fcp_v2", fcp_v2)
        result = self.apply_checks("enum", map(lambda x: (x,), fcp_v2.enums))
        result = self.apply_checks("struct", map(lambda x: (x,), fcp_v2.structs))

        return result


class Verifier(BaseVerifier):
    def __init__(self, sources: Dict[str, str]) -> None:
        self.error_logger = ErrorLogger(sources)

    def check_fcp_v2_duplicate_typenames(self, fcp_v2: Any) -> Result:
        def naming(x: Any) -> Any:
            return x.name

        duplicates = list(
            Verifier.get_duplicates(fcp_v2.structs + fcp_v2.enums, naming, naming)
        )

        if len(duplicates) == 0:
            return Ok(())
        else:
            return Err(
                self.error_logger.log_duplicates(
                    "Found duplicate typenames in fcp configuration", duplicates
                )
            )

    def check_struct_duplicate_signals(self, struct: Any) -> Result:
        def naming(x: Any) -> Any:
            return x.name

        duplicates = list(Verifier.get_duplicates(struct.signals, naming, naming))
        if len(duplicates) == 0:
            return Ok(())
        else:
            return Err(
                self.error_logger.log_duplicates(
                    f"Found duplicate signals in struct {struct.name}",
                    duplicates,
                )
            )

    # def check_signal_type(self, signal: Any) -> Union[Ok, Error]:
    #    types = [
    #        signess + str(width) for signess in ["i", "u"] for width in range(1, 65)
    #    ]
    #    types += ["f32", "f64"]

    #    if signal.type in types:
    #        return Ok(())
    #    else:
    #        return Error(self.error_logger.log_node(signal, "Invalid signal type"))

    @simple_error
    def check_signal_name_is_identifier(self, signal: Any) -> Tuple[bool, str]:
        return (
            not signal.name.isidentifier(),
            f"{signal.name} is not a valid identifier",
        )

    def check_enum_duplicated_values(self, enum: Any) -> Result:
        duplicates = list(
            Verifier.get_duplicates(
                enum.enumeration, lambda x: x.value, lambda x: x.name
            )
        )
        if len(duplicates) == 0:
            return Ok(())
        else:
            return Err(f"Found duplicate values in enum {enum.name}: {duplicates}")

    @simple_error
    def check_enum_name_is_identifier(self, enum: Any) -> Tuple[bool, str]:
        return not enum.name.isidentifier(), f"{enum.name} is not a valid identifier"

    @simple_error
    def check_broadcast_name_is_identifier(self, broadcast: Any) -> Tuple[bool, str]:
        return (
            not broadcast.name.isidentifier(),
            f"{broadcast.name} is not a valid identifier",
        )

    @simple_error
    def check_device_name_is_identifier(self, device: Any) -> Tuple[bool, str]:
        return (
            not device.name.isidentifier(),
            f"{device.name} is not a valid identifier",
        )

    @staticmethod
    def get_duplicates(
        container: Any, selector: Any, naming: Any
    ) -> Generator[Any, None, None]:
        selection = list(map(selector, container))

        count = Counter(selection)
        duplicates = list(filter(lambda x: x[1] > 1, count.items()))

        for duplicate in duplicates:
            for node, value in zip(container, selection):
                if value == duplicate[0]:
                    yield node
