from ..idl import *
from ..validator import *
import pytest

import os

from pathlib import Path


def test_f():
    samples = Path("fcp/tests/v2_samples")
    for path in samples.iterdir():
        spec = Spec()
        j = fcp_v2_from_file(path)
        spec.decompile(j)

        failed = validate(spec)

        assert len(failed) == 0
