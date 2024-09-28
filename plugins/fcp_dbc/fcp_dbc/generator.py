from beartype.typing import Any, Union, Dict
from pathlib import Path

from fcp.codegen import CodeGenerator
from fcp.verifier import Verifier, register
from fcp.result import Result, Err, Ok
from fcp import FcpV2
from fcp.error import FcpError

from .dbc_writer import write_dbc


class Generator(CodeGenerator):
    def __init__(self) -> None:
        pass

    def generate(self, fcp: FcpV2, ctx: Any) -> Dict[str, Union[str, Path]]:
        return [
            {
                "type": "file",
                "path": Path(ctx.get("output")),
                "contents": write_dbc(fcp).unwrap(),
            }
        ]

    def register_checks(self, verifier):
        @register(verifier, "extension")
        def check_extension_valid_type(self, fcp: FcpV2, extension: Any) -> Result:
            struct = fcp.get_struct(extension.type)
            if struct.is_nothing():
                return Err(
                    FcpError(
                        f"No matching type for extension {extension.name}",
                        node=extension,
                    )
                )
            else:
                return Ok(())
