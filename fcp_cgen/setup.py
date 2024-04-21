from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

print(find_packages())

setup(
    name="fcp_cgen",
    description="C code generator for fcp suitable for embedded targets",
    version="0.1",
    author="Joao Freitas",
    author_email="joaj.freitas@gmail.com",
    license="GPLv3",
    url="https://gitlab.com/joajfreitas/fcp-cgen",
    packages=find_packages(),
    install_requires=[
        "fcp"
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
