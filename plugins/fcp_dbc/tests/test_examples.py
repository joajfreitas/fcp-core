import pytest
from fcp.v2_parser import get_fcp


@pytest.mark.parametrize("test_path", ["plugins/fcp_dbc/example/example.fcp"])  # type: ignore
def test_example(test_path: str) -> None:
    fcp_v2, _ = get_fcp(test_path).unwrap()
