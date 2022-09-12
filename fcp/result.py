import logging
import sys
import traceback

from functools import wraps


class ResultShortcutError(Exception):
    def __init__(self, error):
        super().__init__()
        self.error = error


class OptionShortcutError(Exception):
    pass


def result_shortcut(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ResultShortcutError as err:
            return err.error

    return wrapper


class Result:
    def is_err(self):
        return isinstance(self, Error)

    def is_ok(self):
        return isinstance(self, Ok)


class Ok(Result):
    def __init__(self, value):
        self.value = value

    def unwrap(self):
        return self.value

    def err(self):
        sys.exit(1)

    def compound(self, result):
        if isinstance(result, Ok):
            v1 = self.value if isinstance(self.value, list) else [self.value]
            v2 = result.value if isinstance(result.value, list) else [result.value]
            return Ok(v1 + v2)
        else:
            return result

    def Q(self):
        return self.value

    def __repr__(self):
        return "Ok"


class Error(Result):
    def __init__(self, error):
        self.error = error

    def unwrap(self):
        error = self.error if isinstance(self.error, list) else [self.error]

        traceback.print_stack()
        for err in error:
            logging.error(err)
        sys.exit(1)

    def err(self):
        return self.error

    def compound(self, result):
        if isinstance(result, Error):
            v1 = self.error if isinstance(self.error, list) else [self.error]
            v2 = result.error if isinstance(result.error, list) else [result.error]
            return Error(v1 + v2)
        else:
            return self

    def Q(self):
        raise OptionShortcutError(self)

    def __repr__(self):
        error = self.error if isinstance(self.error, list) else [self.error]
        return "Error:\n" + "\n".join(error)
