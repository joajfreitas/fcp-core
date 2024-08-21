from fcp.codegen import CodeGenerator
from fcp.verifier import BaseVerifier, simple_error


class Verifier(BaseVerifier):
    pass


class Generator(CodeGenerator):
    def __init__(self):
        pass

    def generate(self, fcp, templates={}, skels={}):
        print(fcp)
        return {}
