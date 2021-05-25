from setuptools import setup, find_packages

with open("fcp/version.py") as f:
    version = f.read()

_, version = version.split("=")
version = version.strip()

version = version[1:-1]

with open("README.md") as f:
    long_description = f.read()

setup(
    name="fcp",
    description="CAN bus manager",
    version=version,
    author="Joao Freitas",
    author_email="joaj.freitas@gmail.com",
    license="GPLv3",
    url="https://gitlab.com/joajfreitas/fcp-core",
    #download_url="https://gitlab.com/joajfreitas/fcp-core/-/archive/v0.32/fcp-core-v0.29.tar.gz",
    packages=find_packages(),
    entry_points={"console_scripts": ["fcp = fcp.__main__:main",],},
    install_requires=["jinja2", "click", "pyside2", "colorful", "cantools",
                      "hjson", "pyyaml", "PySide2", "sqlalchemy", "appdirs", "result", "hypothesis", "requests", "parsimonious"],
    long_description=long_description,
    long_description_content_type="text/markdown"
)
