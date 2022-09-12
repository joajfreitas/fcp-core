import logging
import sys
from functools import reduce
from collections import Counter

from .result import Ok, Error


class Verifier:
    def __init__(self):
        pass

    @staticmethod
    def check_fcp_v2_duplicate_typenames(fcp_v2):
        duplicates = list(
            Verifier.get_duplicates(
                fcp_v2.structs + fcp_v2.enums, lambda x: x.name, lambda x: x.name
            )
        )
        if len(duplicates) == 0:
            return Ok(())
        else:
            return Error(
                f"Found duplicate typenames in fcp configuration: {duplicates}"
            )

    @staticmethod
    def check_fcp_v2_duplicate_broadcasts(fcp_v2):
        duplicates = list(
            Verifier.get_duplicates(
                fcp_v2.broadcasts, lambda x: x.name, lambda x: x.name
            )
        )
        if len(duplicates) == 0:
            return Ok(())
        else:
            return Error(
                f"Found duplicate broadcasts in fcp configuration: {duplicates}"
            )

    @staticmethod
    def check_struct_duplicate_signals(struct):
        duplicates = list(
            Verifier.get_duplicates(struct.signals, lambda x: x.name, lambda x: x.name)
        )
        if len(duplicates) == 0:
            return Ok(())
        else:
            return Error(
                f"Found duplicate singals in struct {struct.name}: {duplicates}"
            )

    @staticmethod
    def check_signal_type(signal):
        types = [
            signess + str(width) for signess in ["i", "u"] for width in range(1, 65)
        ]
        types += ["f32", "f64"]

        if signal.type in types:
            return Ok(())
        else:
            return Error(f"type {signal.type} is not a valid type")

    @staticmethod
    def check_enum_duplicated_values(enum):
        duplicates = list(
            Verifier.get_duplicates(
                enum.enumeration.items(), lambda x: x[1], lambda x: x[0]
            )
        )
        if len(duplicates) == 0:
            return Ok(())
        else:
            return Error(f"Found duplicate values in enum {enum.name}: {duplicates}")

    @staticmethod
    def get_duplicates(container, selector, naming):
        selection = list(map(selector, container))

        count = Counter(selection)
        duplicates = list(filter(lambda x: x[1] > 1, count.items()))

        for duplicate in duplicates:
            for name, value in zip(map(naming, container), selection):
                if value == duplicate[0]:
                    yield name

    def apply_check(self, category, value):
        result = Ok(())
        for name, f in Verifier.__dict__.items():
            if name.startswith(f"check_{category}"):
                result = result.compound(f(value))

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
