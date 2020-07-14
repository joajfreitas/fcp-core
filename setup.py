from setuptools import setup, find_packages


with open("fcp/version.py") as f:
    version = f.read()

_, version = version.split("=")
version = version.strip()

version = version[1:-1]

setup(
    name="fcp",
    description="CAN bus manager",
    version=version,
    author="Joao Freitas",
    author_email="joaj.freitas@gmail.com",
    license="GPLv3",
    url="https://github.com/joajfreitas/fcp",
    download_url="https://github.com/joajfreitas/fcp/archive/v0.1.tar.gz",
    packages=find_packages(),
    entry_points={"console_scripts": ["fcp = fcp.__main__:main",],},
    install_requires=["click", "PySide2", "jinja2", "ww", "fst_cantools"],
)
