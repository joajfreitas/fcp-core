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

from .dbc_reader import read_dbc
from .dbc_writer import write_dbc
from .specs import FcpV2
from .specs.v1 import FcpV1, fcp_v1_to_v2

from .docs import generate_docs
from .version import VERSION
from .v2_parser import get_fcp
from .codegen import GeneratorManager
from .verifier import Verifier


def setup_logging():
    logging.getLogger().setLevel(logging.DEBUG)
    coloredlogs.install(
        fmt="%(asctime)s %(module)s:%(lineno)d %(levelname)s - %(message)s"
    )


@click.command(name="read-dbc")
@click.argument("dbc")
@click.argument("json_file")
@click.argument("device_config")
def read_dbc_cmd(dbc: str, json_file: str, device_config: str):
    """Transform a DBC file into FCP json.
    :param dbc: dbc file path.
    :param json_file: FCP json file path.
    :param device_config: json with device name configuration.

    device_config example:

    ```json
    {
        "0": "amk_0",
        "1": "amk_1",
        "2": "amk_2",
        "3": "amk_3",
        "8": "dcu",
        "9": "te",
        "10": "dash",
        "13": "arm",
        "14": "bms_master",
        "15": "bms_verbose",
        "16": "iib",
        "20": "ahrsf",
        "21": "ahrsr",
        "22": "gpsf",
        "23": "gpsr",
        "29": "isa"
    }```
    """
    read_dbc(dbc, json_file, device_config)


@click.command(name="generate")
@click.argument("generator")
@click.argument("fcp")
@click.argument("fpi")
@click.argument("output")
@click.argument("templates")
@click.argument("skel")
@click.option("--noformat", is_flag=True, default=False)
@click.option("--force", is_flag=True, default=False)
def generate_cmd(
    generator,
    fcp,
    fpi,
    output: str,
    templates: str,
    skel: str,
    noformat: bool,
    force: bool,
):

    fcp_v2, sources = get_fcp(fcp, fpi).unwrap()
    fcp_v2 = fcp_v2.unwrap()

    Verifier(sources).verify(fcp_v2).unwrap()

    generator_manager = GeneratorManager()
    generator_manager.generate(generator, templates, skel, fcp_v2, sources).unwrap()

    if noformat == False:
        subprocess.run(
            "clang-format -i -style=Webkit *.c *.h",
            cwd=os.path.abspath(output),
            shell=True,
        )
        logging.info("clang-format clean up ✅")


@click.command(name="init")
@click.argument("json_file")
def init_cmd(json_file: str):
    """Create a basic FCP json file.
    :param json_file: FCP json file path.
    """

    # init(json_file, logger)


@click.command(name="validate")
@click.argument("json_file")
def validate_cmd(json_file: str):
    """Verify correctness of FCP json file.
    :param json_file: FCP json file path.
    """

    with open(json_file) as f:
        spec = FcpV1.from_json(f.read())

    spec = spec.to_v2()

    print(spec.to_fcp())
    # spec = get_spec(json_file)
    # print(spec)

    # failed = validate(spec)
    # if len(failed) == 0:
    #    print("✓ JSON validated")
    # else:
    #    print("❌")
    #    for level, msg in failed:
    #        print(format_error(level, msg))


@click.command("json_to_fcp2")
@click.argument("fcp")
@click.argument("fpi")
@click.argument("output")
def json_to_fcp2(fcp: str, fpi: str, output: str):

    fcp_v2, sources = get_fcp(fcp, fpi).unwrap()
    fcp_v2 = fcp_v2.unwrap()

    Verifier(sources).verify(fcp_v2).unwrap()

    output = Path(output)
    with open(output / "main.fcp", "w") as f:
        f.write(fcp_v2.to_fcp())

    with open(output / "main.fpi", "w") as f:
        f.write(fcp_v2.to_fpi())


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, default=False)
def main(version):
    """CLI utility for managment of FCP JSON files."""

    if len(sys.argv) == 1:
        print("fcp cli util.\nVersion:", VERSION, "\nFor usage see fcp --help")
    if version:
        click.echo(VERSION)
    pass


main.add_command(read_dbc_cmd)
main.add_command(generate_cmd)
main.add_command(init_cmd)
main.add_command(validate_cmd)
main.add_command(json_to_fcp2)

if __name__ == "__main__":
    setup_logging()
    main()  # pylint: disable=no-value-for-parameter
