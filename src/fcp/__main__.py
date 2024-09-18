""" Main """

import sys
import logging
import coloredlogs

import click

from .version import VERSION
from .v2_parser import get_fcp
from .codegen import GeneratorManager
from .verifier import Verifier


def setup_logging() -> None:
    logging.getLogger().setLevel(logging.DEBUG)
    coloredlogs.install(
        fmt="%(asctime)s %(module)s:%(lineno)d %(levelname)s - %(message)s"
    )


@click.command(name="generate")
@click.argument("generator")
@click.argument("fcp")
@click.argument("output")
@click.option("--templates")
@click.option("--skel")
@click.option("--noformat", is_flag=True, default=False)
def generate_cmd(
    generator: str,
    fcp: str,
    output: str,
    templates: str,
    skel: str,
    noformat: bool,
) -> None:
    fcp_v2, sources = get_fcp(fcp).unwrap()
    fcp_v2 = fcp_v2.unwrap()

    Verifier(sources).verify(fcp_v2).unwrap()

    generator_manager = GeneratorManager()
    generator_manager.generate(
        generator, templates, skel, fcp_v2, sources, output
    ).unwrap()


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, default=False)
def main(version: str) -> None:
    """CLI utility for managment of FCP JSON files."""

    if len(sys.argv) == 1:
        print("fcp cli util.\nVersion:", VERSION, "\nFor usage see fcp --help")
    if version:
        click.echo(VERSION)


main.add_command(generate_cmd)

if __name__ == "__main__":
    setup_logging()
    main()  # pylint: disable=no-value-for-parameter
