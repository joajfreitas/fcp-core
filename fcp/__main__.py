""" Main """

import sys
import json
import subprocess
import os
from pathlib import Path
import traceback
from pprint import pprint
import logging
import coloredlogs

import click

from . import FcpV2
from .specs.v1 import FcpV1, fcp_v1_to_v2

from .version import VERSION
from .v2_parser import get_fcp
from .codegen import GeneratorManager
from .verifier import Verifier
from .writers import FpiWriter, FcpWriter


def setup_logging():
    logging.getLogger().setLevel(logging.DEBUG)
    coloredlogs.install(
        fmt="%(asctime)s %(module)s:%(lineno)d %(levelname)s - %(message)s"
    )


@click.command(name="generate")
@click.argument("generator")
@click.argument("fcp")
@click.argument("fpi")
@click.argument("output")
@click.option("--templates")
@click.option("--skel")
@click.option("--noformat", is_flag=True, default=False)
def generate_cmd(
    generator,
    fcp,
    fpi,
    output: str,
    templates: str,
    skel: str,
    noformat: bool,
):

    fcp_v2, sources = get_fcp(fcp, fpi).unwrap()
    fcp_v2 = fcp_v2.unwrap()

    Verifier(sources).verify(fcp_v2).unwrap()

    generator_manager = GeneratorManager()
    generator_manager.generate(
        generator, templates, skel, fcp_v2, sources, output
    ).unwrap()


@click.command("json_to_fcp2")
@click.argument("json")
@click.argument("output")
def json_to_fcp2(json: str, output: str):

    logging.info(f"Convertion fcp v1 -> fcp v2. {json} -> {output}")
    with open(json) as f:
        fcp_v1 = FcpV1.from_json(f.read())

    fcp_v2 = fcp_v1.to_v2()

    FcpWriter(output).write(fcp_v2.to_fcp())
    FpiWriter(output).write(fcp_v2.to_fpi())


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, default=False)
def main(version):
    """CLI utility for managment of FCP JSON files."""

    if len(sys.argv) == 1:
        print("fcp cli util.\nVersion:", VERSION, "\nFor usage see fcp --help")
    if version:
        click.echo(VERSION)
    pass


main.add_command(generate_cmd)
main.add_command(json_to_fcp2)

if __name__ == "__main__":
    setup_logging()
    main()  # pylint: disable=no-value-for-parameter
