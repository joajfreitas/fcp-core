# Configuration file for the Sphinx documentation builder.
import sys
import os

# -- Project information

project = "fcp"
copyright = "2024, fcp AUTHORS"

release = "1.0.0"
version = "1.0.0"

# -- General configuration

sys.path.append(os.path.abspath("./_ext"))

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "fcp_lexer",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

templates_path = ["_templates"]

# -- Options for HTML output

html_theme = "sphinx_rtd_theme"

# -- Options for EPUB output
epub_show_urls = "footnote"
