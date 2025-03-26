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

"""Method."""

from serde import serde, strict, to_dict, field
from beartype.typing import Dict, Any, Optional
from .metadata import MetaData


@serde(type_check=strict)
class Method:
    """Method AST node."""

    name: str
    id: int
    input: str
    output: str
    meta: Optional[MetaData] = field(skip=True)

    def reflection(self) -> Dict[str, Any]:
        """Reflection."""
        return {
            "name": self.name,
            "id": self.id,
            "input": self.input,
            "output": self.output,
            "meta": self.meta.reflection() if self.meta else None,
        }

    def __repr__(self) -> str:
        return str(to_dict(self))
