# Copyright (c) 2024 the fcp AUTHORS.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Main."""

import sys
import logging
import coloredlogs
from pprint import pprint

import click

from .version import VERSION
from .v2_parser import get_fcp
from .codegen import GeneratorManager
from .verifier import make_general_verifier
from .error_logger import ErrorLogger
from .serde import encode as serde_encode
from .serde import decode as serde_decode


def setup_logging() -> None:
    """Setup logger."""
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
    """Run generator."""
    fcp_v2, sources = get_fcp(fcp).unwrap()
    generator_manager = GeneratorManager(make_general_verifier())
    result = generator_manager.generate(
        generator, templates, skel, fcp_v2, sources, output
    )

    if result.is_err():
        error_logger = ErrorLogger(sources)
        print(error_logger.log_fcp_error(result.err()))


@click.command()  # type: ignore
@click.argument("fcp")  # type: ignore
def show(fcp: str) -> None:
    """Show fcp schema as dictionary."""
    fcp_result = get_fcp(fcp)

    if fcp_result.is_ok():
        fcp_v2, _ = fcp_result.unwrap()
        pprint(fcp_v2.to_dict())
    else:
        print(fcp_result)


@click.command()  # type: ignore
@click.argument("fcp_schema")  # type: ignore
@click.argument("fcp_data")  # type: ignore
@click.argument("output")  # type: ignore
def encode(fcp_schema: str, fcp_data: str, output: str) -> None:
    """Encode an .fcp according to the data in the reflection schema."""
    fcp_schema, _ = get_fcp(fcp_schema).unwrap()
    fcp_data, _ = get_fcp(fcp_data).unwrap()
    bytearray = serde_encode(fcp_schema, "Fcp", fcp_data.reflection())  # type: ignore

    with open(output, "wb") as f:
        f.write(bytearray)


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
main.add_command(encode)

if __name__ == "__main__":
    setup_logging()
    main()  # pylint: disable=no-value-for-parameter
