import logging
import sys

class Result:
    def is_err(self):
        return isinstance(self, Error)

    def is_ok(self):
        return isinstance(self, Ok)

    def format(value):
        if isinstance(value, list):
            for v in value:
                yield v
        else:
            yield value
    
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

    def __repr__(self):
        return "Ok"

class Error(Result):
    def __init__(self, error):
        self.error = error

    def unwrap(self):
        for err in Result.format(self.error):
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

    def __repr__(self):
        error = self.error if isinstance(self.error, list) else [self.error]
        return "Error:\n" + "\n".join(error)

