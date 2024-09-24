from pprint import pprint
from fcp.codegen import CodeGenerator
from fcp.verifier import BaseVerifier

from .dbc_writer import write_dbc


class Verifier(BaseVerifier):
    pass


class Generator(CodeGenerator):
    def __init__(self):
        pass

    def generate(self, fcp, templates={}, skels={}):
        print(write_dbc(fcp))
        return {}
