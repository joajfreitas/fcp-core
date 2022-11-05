from setuptools import setup

setup(
    name="fcp_v1_gen",
    description="Generator for v1 configuration",
    version="0.1",
    author="Joao Freitas",
    author_email="joaj.freitas@gmail.com",
    license="GPLv3",
    url="https://gitlab.com/joajfreitas/fcp-core",
    packages=["fcp_v1_gen"],
    install_requires=["fcp"],
)
