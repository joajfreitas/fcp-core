import sys
from pathlib import Path


def get_reflection_path():
    return (
        Path(__file__).parent.parent.parent / "reflection" / "reflection.fcp"
    ).resolve()
