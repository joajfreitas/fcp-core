""" Main """

import sys
import logging
import json
import subprocess
import os
from pathlib import Path
import traceback
from pprint import pprint

import click

from .dbc_reader import read_dbc
from .dbc_writer import write_dbc
from .c_generator import c_gen
from .validator import validate, format_error
from .specs import Spec
from .specs.v1 import FcpV1, fcp_v1_to_v2
from .docs import generate_docs
from .version import VERSION
from .idl import fcp_v2
from .v2_parser import get_fcp
from .codegen import GeneratorManager


def setup_logging() -> logging.Logger:
    """Setup Logger.

    :return: logger object.
    """

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    handler = logging.FileHandler("fcp.log")
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def report_validate(failed, force):
    error = 0
    if len(failed):
        for level, msg in failed:
            print(format_error(level, msg))

            if level == "error":
                error += 1

        if error > 0:
            if not force:
                print("Too many error won't continue")
                return True

    return False


def get_spec(schema_path: str, force: bool = False) -> Spec:
    """Create Spec from json file path.
    :param json_file: path to the json file.
    :param logger: logger.
    :return: Spec.
    """
    try:
        path = Path(schema_path)
        if path.suffix == ".json":
            with open(path) as f:
                spec = Spec.from_json(f.read())
        elif path.suffix == ".fcp":
            with open(path) as f:
                spec = fcp_v2(f.read())

        # failed = validate(spec)
        # if report_validate(failed, force):
        #    exit()

        return spec

    except Exception as e:
        print(traceback.format_exc())
        print("error", e.message, ":", e.value)


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
    logger = setup_logging()
    read_dbc(dbc, json_file, device_config, logger)


@click.command(name="write-dbc")
@click.argument("json_file")
@click.argument("dbc")
def write_dbc_cmd(json_file: str, dbc: str):
    """Transform FCP json file into a DBC
    :param json_file: FCP json file path.
    :param dbc: dbc file path.
    """

    spec = get_spec(json_file)
    write_dbc(spec, dbc)


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
        generator, fcp, fpi, output: str, templates: str, skel: str, noformat: bool, force: bool
):
    logger = setup_logging()

    fcp = get_fcp(fcp, fpi)
    generator_manager = GeneratorManager()
    generator_manager.generate(generator, templates, skel, fcp)

    if noformat == False:
        subprocess.run(
            "clang-format -i -style=Webkit *.c *.h",
            cwd=os.path.abspath(output),
            shell=True,
        )
        logger.info("clang-format clean up ✅")


@click.command(name="init")
@click.argument("json_file")
def init_cmd(json_file: str):
    """Create a basic FCP json file.
    :param json_file: FCP json file path.
    """

    logger = setup_logging()
    # init(json_file, logger)


@click.command(name="validate")
@click.argument("json_file")
def validate_cmd(json_file: str):
    """Verify correctness of FCP json file.
    :param json_file: FCP json file path.
    """

    logger = setup_logging()
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


@click.command("docs")
@click.argument("json_file")
@click.argument("out")
@click.argument("link_location", required=False)
def docs(json_file: str, out: str, link_location: str):
    """Generate FCP documentation.
    :param json_file: FCP json file path.
    :param out: output directory.
    """

    if link_location == None:
        link_location = "."

    logger = setup_logging()

    spec = get_spec(json_file)
    generate_docs(spec, out, link_location, logger)


@click.command("fix")
@click.argument("src")
@click.argument("dst")
def fix(src: str, dst: str):
    print("Warning: This operation may lose some data")
    spec = Spec()
    with open(src) as f:
        j = json.loads(f.read())

    spec.decompile(j)

    for dev in spec.devices.values():
        for msg in dev.msgs.values():
            for sig in msg.signals.values():
                if sig.mux_count == 0:
                    sig.mux_count = 1

    d = spec.compile()
    with open(dst, "w") as f:
        f.write(json.dumps(d, indent=4))


@click.command("json_to_fcp2")
@click.argument("json_file")
@click.argument("output")
def json_to_fcp2(json_file: str, output: str):

    with open(json_file) as f:
        fcp_v1 = FcpV1.from_json(f.read())

    fcp_v2 = fcp_v1_to_v2(fcp_v1)

    with open(output, "w") as f:
        f.write(fcp_v2.to_idl())

    # spec = get_spec(json_file)
    # v2 = spec_to_fcp_v2(spec)

    # with open(output, "w") as f:
    #    f.write(v2)


@click.command("fcp2_to_json")
@click.argument("fcpv2")
@click.argument("fcpv1")
def fcp2_to_json(fcpv2: str, fcpv1: str):
    spec = get_spec(fcpv2)
    with open(fcpv1, "w") as f:
        f.write(json.dumps(spec.compile(), indent=4))

@click.command("parse")
@click.argument("fcp")
@click.argument("fpi")
def parse(fcp, fpi):
    fcp = get_fcp(fcp, fpi)
    pprint(fcp.to_dict())



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
main.add_command(write_dbc_cmd)
main.add_command(generate_cmd)
main.add_command(init_cmd)
main.add_command(validate_cmd)
main.add_command(docs)
main.add_command(fix)
main.add_command(json_to_fcp2)
main.add_command(fcp2_to_json)
main.add_command(parse)

if __name__ == "__main__":
    main()
