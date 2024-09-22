# _ext/fcp_lexer.py

from pygments.lexers.python import PythonLexer


def setup(app):
    # choose one, both ok
    app.add_lexer("fcp", PythonLexer)
