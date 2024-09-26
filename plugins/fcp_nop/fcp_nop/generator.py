from pprint import pprint
from beartype.typing import Any, Dict
from fcp.codegen import CodeGenerator
from fcp.verifier import BaseVerifier
from fcp import FcpV2


class Verifier(BaseVerifier):
    pass


class Generator(CodeGenerator):
    def __init__(self) -> None:
        pass

    def generate(
        self, fcp: FcpV2, templates: Any = {}, skels: Any = {}
    ) -> Dict[str, str]:
        pprint(fcp.to_dict())

        return {}
