from ..idl import *
from ..validator import *
import pytest

import os


def test_f():
    for path in os.listdir("fcp/tests/v2_samples"):
        spec = Spec()
        j = fcp_v2_from_file(path)
        spec.decompile(j)

        failed = validate(spec)

        assert len(failed) == 0
