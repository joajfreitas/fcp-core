# Copyright (c) 2024 the fcp AUTHORS.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Generator."""

from beartype.typing import Any, Union, Dict, NoReturn
from pathlib import Path

from fcp.codegen import CodeGenerator
from fcp.verifier import register, Verifier
from fcp.result import Result, Ok
from fcp.specs.v2 import FcpV2
from fcp.error import FcpError, error
from fcp.types import Nil
from fcp.specs.impl import Impl

from .dbc_writer import write_dbc


class Generator(CodeGenerator):
    """DBC generator."""

    def __init__(self) -> None:
        pass

    def generate(self, fcp: FcpV2, ctx: Any) -> Dict[str, Union[str, Path]]:
        """Generate dbc files."""
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
        """Register dbc specific checks."""

        @register(verifier, "impl")  # type: ignore
        def check_impl_valid_type(
            self: Any, fcp: FcpV2, impl: Impl
        ) -> Result[Nil, FcpError]:
            struct = fcp.get_struct(impl.type)
            if struct.is_nothing():
                return error(
                    f"No matching type for impl {impl.name}",
                    node=impl,
                )
            else:
                return Ok(())

        @register(verifier, "impl")  # type: ignore
        def check_duplicate_can_ids(
            self: Any, fcp: FcpV2, impl: Impl
        ) -> Result[Nil, FcpError]:
            impl_ids = [impl.fields.get("id") for impl in fcp.impls]
            if impl_ids.count(impl.fields.get("id")) > 1:
                return error("Duplicate ids", node=impl)
            else:
                return Ok(())
