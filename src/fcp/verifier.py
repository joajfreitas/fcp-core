"""Verifier."""

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

from beartype.typing import Callable, NoReturn, Dict, Optional, Any, Tuple
from .result import Ok, Result, Err
from .maybe import catch
from .error import FcpError
from .types import Nil
from .specs.v2 import FcpV2
from .specs.impl import Impl
from .specs.struct_field import StructField
from .specs.struct import Struct
from .specs.enum import Enum


class Verifier:
    """Verifies fcp AST.

    Allows registering custom checks via the register decorator.
    """

    def __init__(self) -> None:
        """Construct a Verifier."""
        self.categories = [
            "struct",
            "field",
            "enum",
            "impl",
            "signal_block",
            "type",
            "uncategorized",
        ]
        self.checks: Dict[str, Callable] = {
            category: [] for category in self.categories
        }

    def register(self, function: Callable, category: Optional[str] = None) -> NoReturn:
        """Register a check in the verifier. Optionally, the check can be categorized.

        Available categories:

        * struct
        * field
        * enum
        * impl
        * signal_block
        * type

        """
        if category is None:
            self.checks["uncategorized"].append(function)
            return

        if category not in self.categories:
            raise ValueError(f"Invalid category: {category}")
        self.checks[category].append(function)

    @catch
    def run_checks(self, category: str, fcp: FcpV2) -> Result[Nil, FcpError]:
        """Run check for a category."""
        for check in self.checks.get(category) or []:
            for node in fcp.get(category).attempt():
                check(fcp, fcp, node).attempt()

        return Ok(())

    @catch
    def verify(self, fcp: FcpV2) -> Result[Nil, FcpError]:
        """Run the checks."""
        for category in self.categories:
            self.run_checks(category, fcp).attempt()

        return Ok(())


def register(verifier: Verifier, category: Optional[str] = None) -> Callable:
    """Register a check. Function decorator.

    :param Verifier verifier: The verifier object where the check will be registered.
    :param Optional[str] category: Verification category. Determines which object type is given to the decorated function.

    Categories can be:

        * struct
        * field
        * enum
        * impl
        * signal_block
        * type

    Each category correspondes to a fcp node type. Exception for 'type' which is an union of 'struct' and 'enum' categories.

    .. code-block:: python

        @register(verfier, 'struct')
        def verify_struct_name(self: Verifier, fcp: FcpV2, struct: Struct):
            return struct.name == "mandatory_name"
    """

    def decorator(f: Callable) -> Callable:
        verifier.register(f, category)
        return f

    return decorator


def make_general_verifier() -> Verifier:
    """Create verifier that applies verication rules valid for any fcp schema."""
    general_verifier = Verifier()

    @register(general_verifier, "type")  # type: ignore
    def check_duplicate_typenames(
        self: Any, fcp: FcpV2, type: Any
    ) -> Result[Nil, FcpError]:
        type_names = [type.name for type in fcp.get_types()]

        if type_names.count(type.name) > 1:
            return Err(FcpError("Duplicate type names", node=type))
        else:
            return Ok(())

    @register(general_verifier, "impl")  # type: ignore
    def check_duplicate_impl(
        self: Any, fcp: FcpV2, left: Impl
    ) -> Result[Nil, FcpError]:
        impls = [(impl.name, impl.protocol) for impl in fcp.impls]
        if impls.count((left.name, left.protocol)) > 1:
            return Err(FcpError("Duplicate impls", node=left))
        else:
            return Ok(())

    @register(general_verifier, "field")  # type: ignore
    def check_duplicate_struct_fields(
        self: Any, fcp: FcpV2, left: Tuple[Struct, StructField]
    ) -> Result[Nil, FcpError]:
        struct, left_signal = left
        signal_names = [field.name for field in struct.fields]
        if signal_names.count(left_signal.name) > 1:
            return Err(FcpError("Duplicate fields", node=left_signal))
        else:
            return Ok(())

    @register(general_verifier, "struct")  # type: ignore
    def check_struct_contains_struct_fields(
        self: Any, fcp: FcpV2, struct: Struct
    ) -> Result[Nil, FcpError]:
        if len(struct.fields) == 0:
            return Err(FcpError("Struct has no signal", node=struct))
        else:
            return Ok(())

    @register(general_verifier, "enum")  # type: ignore
    def check_enum_duplicate_enumerations_names(
        self: Any, fcp: FcpV2, enum: Enum
    ) -> Result[Nil, FcpError]:
        enumeration_names = [enumeration.name for enumeration in enum.enumeration]
        for enumeration in enum.enumeration:
            if enumeration_names.count(enumeration.name) > 1:
                return Err(FcpError("Duplicated enumration name", node=enumeration))

        return Ok(())

    @register(general_verifier, "enum")  # type: ignore
    def check_enum_duplicate_enumerations_values(
        self: Any, fcp: FcpV2, enum: Enum
    ) -> Result[Nil, FcpError]:
        enumeration_names = [enumeration.value for enumeration in enum.enumeration]
        for enumeration in enum.enumeration:
            if enumeration_names.count(enumeration.value) > 1:
                return Err(FcpError("Duplicated enumration name", node=enumeration))

        return Ok(())

    return general_verifier
