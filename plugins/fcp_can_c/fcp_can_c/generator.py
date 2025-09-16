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

"""C code generator for FCP to CAN."""

import os


from beartype.typing import Any, Union, Dict, List
from pathlib import Path

from fcp.codegen import CodeGenerator
from fcp.verifier import register, Verifier
from fcp.result import Result, Ok
from fcp.specs.v2 import FcpV2
from fcp.error import FcpError, error
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

        for filename, contents in writer.generate_rpc_headers():
            files.append(to_dict("file", f"{base_dir}/{filename}_rpc.h", contents))

        for filename, contents in writer.generate_rpc_sources():
            files.append(to_dict("file", f"{base_dir}/{filename}_rpc.c", contents))

        return files

    def register_checks(self, verifier: Verifier) -> None:
        """Register checks in verifier.

        Args:
            verifier: Verifier object

        """

        @register(verifier, "impl")  # type: ignore
        def check_impl_valid_type(
            self: Any, fcp: FcpV2, extension: Any
        ) -> Result[Nil, FcpError]:
            """Check if extension has a valid type."""
            struct = fcp.get_struct(extension.type)
            if struct.is_nothing():
                return error(
                    f"No matching type for extension {extension.name}",
                    node=extension,
                )
            else:
                return Ok(())

        @register(verifier, "impl")  # type: ignore
        def check_impl_size(
            self: Any, fcp: FcpV2, extension: Any
        ) -> Result[Nil, FcpError]:
            """Check if extension has a valid type."""
            struct = fcp.get_struct(extension.type)
            size = sum([field.type.get_length() for field in struct.unwrap().fields])
            if size > 64:
                return error(
                    f"Impl {extension.name} is way too big at {size} bits",
                    node=extension,
                )
            else:
                return Ok(())

        @register(verifier, "struct")  # type: ignore
        def check_field_id_clash(
            self: Any, fcp: FcpV2, extension: Any
        ) -> Result[Nil, FcpError]:
            """Check for duplicate field IDs inside structs."""
            for struct in fcp.structs:
                seen_ids = set()
                for field in struct.fields:
                    if field.field_id in seen_ids:
                        return error(
                            f"Duplicate field ID @{field.field_id} in struct '{struct.name}'",
                            node=field,
                        )
                    seen_ids.add(field.field_id)
            return Ok(())

        @register(verifier, "impl")  # type: ignore
        def check_service_method_id_clash(
            self: Any, fcp: FcpV2, extension: Any
        ) -> Result[Nil, FcpError]:
            """Check for duplicate method IDs inside services."""
            for service in fcp.services:  # iterate all services
                seen_ids = set()
                for method in service.methods:
                    if method.id in seen_ids:
                        return error(
                            f"Duplicate method ID @{method.id} in service '{service.name}' "
                            f"(method '{method.name}')",
                            node=method,
                        )
                    seen_ids.add(method.id)
            return Ok(())

        @register(verifier, "impl")  # type: ignore
        def check_rpc_method_id_clash(
            self: Any, fcp: FcpV2, extension: Any
        ) -> Result[Nil, FcpError]:
            """Check for duplicate RPC method IDs across all services."""
            seen_ids = {}  # type: ignore[var-annotated]

            for service in fcp.services:
                for method in service.methods:
                    if method.id in seen_ids:
                        return error(
                            f"Duplicate RPC method ID @{method.id} detected in service "
                            f"'{service.name}' (method '{method.name}') "
                            f"and service '{seen_ids[method.id].service_name}' "
                            f"(method '{seen_ids[method.id].name}')",
                            node=method,
                        )
                    # store both method name and service name for reporting
                    method.service_name = service.name
                    seen_ids[method.id] = method

            return Ok(())
