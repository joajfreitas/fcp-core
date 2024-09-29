import json
from beartype.typing import Any, Dict, Union
from pathlib import Path
from fcp.codegen import CodeGenerator
from fcp import FcpV2


class Generator(CodeGenerator):
    def __init__(self) -> None:
        pass

    def generate(self, fcp: FcpV2, ctx: Any) -> Dict[str, Union[str, Path]]:
        return [{"type": "print", "contents": json.dumps(fcp.to_dict(), indent=4)}]
