""" Main """

import sys
import logging
import json
import subprocess
import os
from pathlib import Path

import click

from .dbc_reader import read_dbc
from .dbc_writer import write_dbc
from .c_generator import c_gen
from .validator import validate, format_error
from .specs import Spec
from .docs import generate_docs
from .version import VERSION
from .idl import spec_to_fcp_v2, fcp_v2_from_file, fcp_v2


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


def get_spec(json_file: str, force: bool = False) -> Spec:
    """Create Spec from json file path.
    :param json_file: path to the json file.
    :param logger: logger.
    :return: Spec.
    """

    spec = Spec()

    path = Path(json_file)
    if path.suffix == ".json":
        with open(json_file) as f:
            j = json.loads(f.read())
    elif path.suffix == ".fcp":
        j = fcp_v2_from_file(json_file)

    spec.decompile(j)
    failed = validate(spec)
    if report_validate(failed, force):
        exit()

    return spec


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


@click.command(name="c_gen")
@click.argument("templates")
@click.argument("output")
@click.argument("json_file")
@click.argument("skel")
@click.option("--noformat", is_flag=True, default=False)
@click.option("--force", is_flag=True, default=False)
def c_gen_cmd(templates: str, output: str, json_file: str, skel: str, noformat: bool, force: bool):
    """Transform FCP json into a C library.
    :param templates: jinja template directory.
    :param output: output directory.
    :param json_file: FCP json file path.
    :param skel: C skeleton directory.
    """
    logger = setup_logging()

    spec = get_spec(json_file, force)
    c_gen(spec, templates, output, skel, logger)

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
    spec = get_spec(json_file)

    failed = validate(spec)
    if len(failed) == 0:
        print("✓ JSON validated")
    else:
        print("❌")
        for level, msg in failed:
            print(format_error(level, msg))


@click.command(name="gui")
@click.argument("file", required=False)
def gui_cmd(file: str):
    """Launch FCP json editor GUI.
    :param file: Optional FCP json file path
    """

    from .gui import gui

    logger = setup_logging()
    gui(file)


@click.command(name="gui2")
@click.argument("file", type=Path, required=False)
def gui_cmd2(file: Path):
    """Launch FCP json editor GUI.
    :param file: Optional FCP json file path
    """

    from .gui2 import gui2

    gui2(file)


@click.command()
@click.argument("json_file")
def dump_dev_list(json_file):
    spec = get_spec(json_file)

    for dev in spec.devices.keys():
        print(dev)


@click.command()
@click.argument("json_file")
@click.argument("device", required=False)
def dump_msg_list(json_file, device):
    spec = get_spec(json_file)

    for dev_name, dev in spec.devices.items():
        if device != None and device != dev_name:
            continue

        for msg in dev.msgs.keys():
            print(msg)


@click.command()
@click.argument("json_file")
@click.argument("device", required=False)
def dump_cfg_list(json_file, device):
    spec = get_spec(json_file)

    for dev_name, dev in spec.devices.items():
        if device != None and device != dev_name:
            continue

        for cfg in dev.cfgs.keys():
            print(cfg)


@click.command()
@click.argument("json_file")
@click.argument("device", required=False)
def dump_cmd_list(json_file, device):
    spec = get_spec(json_file)

    for dev_name, dev in spec.devices.items():
        if device != None and device != dev_name:
            continue

        for cmd in dev.cmds.keys():
            print(cmd)


@click.command()
@click.argument("json_file")
def dump_log_list(json_file):
    spec = get_spec(json_file)

    for log in spec.logs.keys():
        print(log)


@click.command()
@click.argument("json_file")
@click.argument("message", required=False)
def dump_signal_list(json_file, message):
    spec = get_spec(json_file)

    for dev in spec.devices.values():
        for msg in dev.msgs.values():
            if message != None and msg.name != message:
                continue
            for signal in msg.signals.values():
                print(signal)


@click.command()
@click.argument("json_file")
@click.argument("message", required=False)
def dump_signal_names(json_file, message):
    spec = get_spec(json_file)

    for dev in spec.devices.values():
        for msg in dev.msgs.values():
            if message != None and msg.name != message:
                continue
            for signal in msg.signals.values():
                print(signal.name)


@click.command()
@click.argument("json_file")
@click.argument("log")
def print_log(json_file, log):
    spec = get_spec(json_file)

    print(spec.get_log(log))


@click.command()
@click.argument("json_file")
@click.argument("dev")
def print_dev(json_file, dev):
    spec = get_spec(json_file)

    print(spec.get_device(dev))


@click.command()
@click.argument("json_file")
@click.argument("message")
def print_msg(json_file, message):
    spec = get_spec(json_file)

    for dev in spec.devices.values():
        for name, msg in dev.msgs.items():
            if name == message:
                print(dev.name)
                print(msg)


@click.command()
@click.argument("json_file")
@click.argument("signal")
def print_signal(json_file, signal):
    spec = get_spec(json_file)

    for dev in spec.devices.values():
        for msg in dev.msgs.values():
            for name, sig in msg.signals.items():
                if name == signal:
                    print(dev.name, msg.name)
                    print(sig)


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
    spec = get_spec(json_file)
    v2 = spec_to_fcp_v2(spec)

    with open(output, "w") as f:
        f.write(v2)



@click.command("read_fcp2")
@click.argument("fcp_v2_file")
def read_fcp2(fcp_v2_file):
    with open(fcp_v2_file) as f:
        v2 = fcp_v2(f.read())

    spec = Spec()
    spec.decompile(v2)


@click.command("read_fcp")
@click.argument("json_file")
def read_fcp(json_file: str):
    logger = setup_logging()

    spec = get_spec(json_file)
    print(spec)



@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, default=False)
def main(version):
    """CLI utility for managment of FCP JSON files. """

    if len(sys.argv) == 1:
        print("fcp cli util.\nVersion:", VERSION, "\nFor usage see fcp --help")
    if version:
        click.echo(VERSION)
    pass


main.add_command(read_dbc_cmd)
main.add_command(write_dbc_cmd)
main.add_command(c_gen_cmd)
main.add_command(init_cmd)
main.add_command(validate_cmd)
main.add_command(gui_cmd)
#main.add_command(dump_dev_list)
#main.add_command(dump_msg_list)
#main.add_command(dump_cfg_list)
#main.add_command(dump_cmd_list)
#main.add_command(dump_log_list)
#main.add_command(dump_signal_list)
#main.add_command(dump_signal_names)
#main.add_command(print_log)
#main.add_command(print_dev)
#main.add_command(print_msg)
#main.add_command(print_signal)
main.add_command(docs)
main.add_command(fix)
main.add_command(json_to_fcp2)
main.add_command(read_fcp2)
main.add_command(read_fcp)

if __name__ == "__main__":
    main()
