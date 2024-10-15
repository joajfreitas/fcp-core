import os

from beartype.typing import Any, Union, NoReturn, Dict
from pathlib import Path

from fcp.codegen import CodeGenerator
from fcp.verifier import register, Verifier
from fcp.result import Result, Err, Ok
from fcp import FcpV2
from fcp.error import FcpError
from fcp.types import Nil

from .can_c_writer import CanCWritter


class Generator(CodeGenerator):
    def __init__(self) -> None:
        pass

    def generate(self, fcp: FcpV2, ctx: Any) -> list[Dict[str, Union[str, Path]]]:
        def to_dict(s1: str, s2: str, s3: str) -> Dict[str, str]:
            return {"type": s1, "path": s2, "contents": s3}

        writer = CanCWritter(fcp)
        base_dir = str(ctx.get("output"))
        files = []

        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        else:
            # Clear the directory
            for file in os.listdir(base_dir):
                os.remove(os.path.join(base_dir, file))

        for filename, contents in writer.gen_static_files():
            files.append(to_dict("file", f"{base_dir}/{filename}", contents))

        for dev_name, contents in writer.gen_device_headers():
            files.append(to_dict("file", f"{base_dir}/{dev_name}_can.h", contents))

        return files

    def register_checks(self, verifier: Verifier) -> None:
        @register(verifier, "extension")  # type: ignore
        def check_extension_valid_type(
            self: Any, fcp: FcpV2, extension: Any
        ) -> Result[Nil, FcpError]:
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
