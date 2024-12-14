"""Helper methods for reflection."""

from pathlib import Path
from beartype.typing import Tuple, Dict

from .v2_parser import get_fcp
from .specs.v2 import FcpV2
from .result import Result


def _get_reflection_path() -> Path:
    return (Path(__file__).parent / "reflection" / "reflection.fcp").resolve()


def get_reflection_schema() -> Result[Tuple[FcpV2, Dict[str, str]], str]:
    """Builds the reflection schema."""
    return get_fcp(_get_reflection_path())  # type: ignore
