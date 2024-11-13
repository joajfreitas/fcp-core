"""C code generator for FCP to CAN."""

import os

from beartype.typing import Any, Union, NoReturn, Dict, List
from pathlib import Path

from fcp.codegen import CodeGenerator
from fcp.verifier import register, Verifier
from fcp.result import Result, Err, Ok
from fcp import FcpV2
from fcp.error import FcpError
from fcp.types import Nil

from .can_c_writer import CanCWriter


class Generator(CodeGenerator):
    """Class for C code from FCP to CAN."""

    def __init__(self) -> None:
        """None."""
        pass

    def generate(self, fcp: FcpV2, ctx: Any) -> List[Dict[str, Union[str, Path]]]:
        """Generate C code from FCP.

        Args:
            fcp: FcpV2 object
            ctx: Context object

        Returns:
            List of dictionaries with file information

        """

        def to_dict(type: str, path: str, contents: str) -> Dict[str, str]:
            """Type, path, contents to a generator dictionary."""
            return {"type": type, "path": path, "contents": contents}

        writer = CanCWriter(fcp)
        base_dir = str(ctx.get("output"))
        files = []

        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        else:
            # Clear the directory
            for file in os.listdir(base_dir):
                if file.endswith(".h") or file.endswith(".c"):
                    os.remove(os.path.join(base_dir, file))

        for filename, contents in writer.generate_static_files():
            files.append(to_dict("file", f"{base_dir}/{filename}", contents))

        for filename, contents in writer.generate_device_headers():
            files.append(to_dict("file", f"{base_dir}/{filename}_can.h", contents))

        for filename, contents in writer.generate_device_sources():
            files.append(to_dict("file", f"{base_dir}/{filename}_can.c", contents))

        return files

    def register_checks(self, verifier: Verifier) -> None:
        """Register checks in verifier.

        Args:
            verifier: Verifier object

        """

        @register(verifier, "extension")  # type: ignore
        def check_extension_valid_type(
            self: Any, fcp: FcpV2, extension: Any
        ) -> Result[Nil, FcpError]:
            """Check if extension has a valid type."""
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
