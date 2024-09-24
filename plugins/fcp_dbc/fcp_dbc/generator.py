from typing import Any

from fcp.codegen import CodeGenerator
from fcp.verifier import BaseVerifier
from fcp import FcpV2

from .dbc_writer import write_dbc


class Verifier(BaseVerifier):
    pass


class Generator(CodeGenerator):
    def __init__(self) -> None:
        pass

    def generate(
        self, fcp: FcpV2, templates: Any = {}, skels: Any = {}
    ) -> dict[str, str]:
        print(write_dbc(fcp))
        return {}
