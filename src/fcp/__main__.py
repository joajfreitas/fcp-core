"""Main"""

import sys
import logging
import coloredlogs
from pprint import pprint

import click

from .version import VERSION
from .v2_parser import get_fcp
from .codegen import GeneratorManager
from .verifier import GeneralVerifier
from .error_logger import ErrorLogger


def setup_logging() -> None:
    logging.getLogger().setLevel(logging.DEBUG)
    coloredlogs.install(
        fmt="%(asctime)s %(module)s:%(lineno)d %(levelname)s - %(message)s"
    )


@click.command(name="generate")  # type: ignore
@click.argument("generator")  # type: ignore
@click.argument("fcp")  # type: ignore
@click.argument("output")  # type: ignore
@click.option("--templates")  # type: ignore
@click.option("--skel")  # type: ignore
def generate_cmd(
    generator: str,
    fcp: str,
    output: str,
    templates: str,
    skel: str,
) -> None:
    fcp_v2, sources = get_fcp(fcp).unwrap()
    generator_manager = GeneratorManager(GeneralVerifier())
    result = generator_manager.generate(
        generator, templates, skel, fcp_v2, sources, output
    )

    if result.is_err():
        error_logger = ErrorLogger(sources)
        print(error_logger.log_fcp_error(result.err()))


@click.command()
@click.argument("fcp")  # type: ignore
def show(fcp):
    fcp_result = get_fcp(fcp)

    if fcp_result.is_ok():
        fcp, sources = fcp_result.unwrap()
        pprint(fcp)
    else:
        print(fcp_result)


@click.group(invoke_without_command=True)  # type: ignore
@click.option("--version", is_flag=True, default=False)  # type: ignore
def main(version: str) -> None:
    """CLI utility for management of FCP JSON files."""

    if len(sys.argv) == 1:
        print("fcp cli util.\nVersion:", VERSION, "\nFor usage see fcp --help")
    if version:
        click.echo(VERSION)


main.add_command(generate_cmd)
main.add_command(show)

if __name__ == "__main__":
    setup_logging()
    main()  # pylint: disable=no-value-for-parameter
