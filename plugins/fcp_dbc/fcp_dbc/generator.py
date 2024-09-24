from typing import Any, Union
from pathlib import Path

from fcp.codegen import CodeGenerator
from fcp.verifier import BaseVerifier
from fcp import FcpV2

from .dbc_writer import write_dbc


class Verifier(BaseVerifier):
    pass


class Generator(CodeGenerator):
    def __init__(self) -> None:
        pass

    def generate(self, fcp: FcpV2, ctx: Any) -> list[str, Union[str, Path]]:
        return [
            {
                "type": "file",
                "path": Path(ctx.get("output")),
                "contents": write_dbc(fcp),
            }
        ]
