import sys
import traceback

from typing import Any, Union
from functools import wraps


class Result:
    def is_err(self) -> bool:
        return isinstance(self, Error)

    def is_ok(self) -> bool:
        return isinstance(self, Ok)


class Ok(Result):
    def __init__(self, value: Any) -> None:
        self.value = value

    def unwrap(self) -> Any:
        return self.value

    def err(self) -> None:
        sys.exit(1)

    def compound(self, result: Any) -> Any:
        if isinstance(result, Ok):
            v1 = self.value if isinstance(self.value, list) else [self.value]
            v2 = result.value if isinstance(result.value, list) else [result.value]
            return Ok(v1 + v2)
        else:
            return result

    def Q(self) -> Any:
        return self.value

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Ok):
            return False

        return bool(self.value == other.value)

    def __repr__(self) -> str:
        return "Ok"


class Error(Result):
    def __init__(self, error: Any) -> None:
        self.error = error if isinstance(error, list) else [error]

    def unwrap(self) -> tuple[None, None]:
        error = self.error

        for err in error:
            print(err)

        traceback.print_stack()
        sys.exit(1)

        return (None, None)

    def err(self) -> list[str]:
        return self.error

    def compound(self, result: Result) -> Union[Ok, Any]:
        if isinstance(result, Error):
            v1 = self.error
            v2 = result.error
            return Error(v1 + v2)
        else:
            return self

    def Q(self) -> None:
        raise ResultShortcutError(self)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Error):
            return False

        return self.error == other.error

    def __repr__(self) -> str:
        error = self.error if isinstance(self.error, list) else [self.error]  # type: ignore
        return "Error:\n" + "\n".join(error)


class ResultShortcutError(Exception):
    def __init__(self, error: Error) -> None:
        super().__init__()
        self.error = error


def result_shortcut(f: Any) -> Any:
    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return f(*args, **kwargs)
        except ResultShortcutError as err:
            return err.error

    return wrapper
