from beartype.typing import Any, Union, Dict, NoReturn
from pathlib import Path

from fcp.codegen import CodeGenerator
from fcp.verifier import register, Verifier
from fcp.result import Result, Err, Ok
from fcp import FcpV2
from fcp.error import FcpError
from fcp.types import Nil
from fcp.specs.impl import Impl

from .dbc_writer import write_dbc


class Generator(CodeGenerator):
    def __init__(self) -> None:
        pass

    def generate(self, fcp: FcpV2, ctx: Any) -> Dict[str, Union[str, Path]]:
        return [
            {
                "type": "file",
                "path": Path(ctx.get("output")) / (bus + ".fcp"),
                "contents": content,
                "bus": bus,
            }
            for bus, content in write_dbc(fcp).unwrap()
        ]

    def register_checks(self, verifier: Verifier) -> NoReturn:
        @register(verifier, "impl")  # type: ignore
        def check_impl_valid_type(
            self: Any, fcp: FcpV2, impl: Impl
        ) -> Result[Nil, FcpError]:
            struct = fcp.get_struct(impl.type)
            if struct.is_nothing():
                return Err(
                    FcpError(
                        f"No matching type for impl {impl.name}",
                        node=impl,
                    )
                )
            else:
                return Ok(())

        @register(verifier, "impl")  # type: ignore
        def check_duplicate_can_ids(
            self: Any, fcp: FcpV2, impl: Impl
        ) -> Result[Nil, FcpError]:
            impl_ids = [impl.fields.get("id") for impl in fcp.impls]
            if impl_ids.count(impl.fields.get("id")) > 1:
                return Err(FcpError("Duplicate ids", node=impl))
            else:
                return Ok(())
