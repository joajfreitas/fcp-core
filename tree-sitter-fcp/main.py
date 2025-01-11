import sys

import tree_sitter_fcp as tsfcp
from tree_sitter import Language, Parser

FCP_LANGUAGE = Language(tsfcp.language())

parser = Parser(FCP_LANGUAGE)

with open(sys.argv[1], "rb") as f:
    r = parser.parse(f.read())

print(r.root_node.children)
