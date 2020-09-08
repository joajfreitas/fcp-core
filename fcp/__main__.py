import sys
import logging
import json
import subprocess, os

import click

from .dbc_reader import read_dbc, init
from .dbc_writer import write_dbc
from .c_generator import c_gen
from .gui import gui
from .validator import validate
from .spec import Spec
from .docs import generate_docs
from .version import VERSION


def setup_logging() -> logging.Logger:
    """ Setup Logger.

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


def get_spec(json_file: str, logger: logging.Logger) -> Spec:
    """Create Spec from json file path.
    :param json_file: path to the json file.
    :param logger: logger.
    :return: Spec.
    """

    spec = Spec()
    with open(json_file) as f:
        j = json.loads(f.read())

    r, msg = validate(logger, j)
    if not r:
        print(msg)
        exit()

    spec.decompile(j)

    return spec


@click.command(name="read-dbc")
@click.argument("dbc")
@click.argument("json_file")
@click.argument("device_config")
def read_dbc_cmd(dbc: str, json_file: str, device_config: str):
    """ Transform a DBC file into FCP json.
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
    """ Transform FCP json file into a DBC
    :param json_file: FCP json file path.
    :param dbc: dbc file path.
    """

    logger = setup_logging()

    with open(json_file) as f:
        j = json.loads(f.read())
    write_dbc(j, dbc, logger)


@click.command(name="c_gen")
@click.argument("templates")
@click.argument("output")
@click.argument("json_file")
@click.argument("skel")
@click.option("--noformat", is_flag=True, default=False)
def c_gen_cmd(templates: str, output: str, json_file: str, skel: str, noformat: bool):
    """Transform FCP json into a C library.
    :param templates: jinja template directory.
    :param output: output directory.
    :param json_file: FCP json file path.
    :param skel: C skeleton directory.
    """

    logger = setup_logging()
    c_gen(templates, output, json_file, skel, logger)

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
    #init(json_file, logger)


@click.command(name="validate")
@click.argument("json_file")
def validate_cmd(json_file: str):
    """Verify correctness of FCP json file.
    :param json_file: FCP json file path.
    """

    logger = setup_logging()
    with open(json_file) as f:
        j = f.read()

    r, msg = validate(logger, json.loads(j))
    if r:
        print("✓ JSON validated")
    else:
        print("❌" + msg)


@click.command(name="gui")
@click.argument("file", required=False)
def gui_cmd(file: str):
    """Launch FCP json editor GUI.
    :param file: Optional FCP json file path
    """
    logger = setup_logging()
    gui(file, logger)

@click.command()
@click.argument("json_file")
def dump_dev_list(json_file):
    logger = setup_logging()
    spec = get_spec(json_file, logger)

    for dev in spec.devices.keys():
        print(dev)


@click.command()
@click.argument("json_file")
@click.argument("device", required=False)
def dump_msg_list(json_file, device):
    logger = setup_logging()

    spec = get_spec(json_file, logger)

    for dev_name, dev in spec.devices.items():
        if device != None and device != dev_name:
            continue

        for msg in dev.msgs.keys():
            print(msg)


@click.command()
@click.argument("json_file")
@click.argument("device", required=False)
def dump_cfg_list(json_file, device):
    logger = setup_logging()

    spec = get_spec(json_file, logger)

    for dev_name, dev in spec.devices.items():
        if device != None and device != dev_name:
            continue

        for cfg in dev.cfgs.keys():
            print(cfg)


@click.command()
@click.argument("json_file")
@click.argument("device", required=False)
def dump_cmd_list(json_file, device):
    logger = setup_logging()

    spec = get_spec(json_file, logger)

    for dev_name, dev in spec.devices.items():
        if device != None and device != dev_name:
            continue

        for cmd in dev.cmds.keys():
            print(cmd)


@click.command()
@click.argument("json_file")
def dump_log_list(json_file):
    logger = setup_logging()
    spec = get_spec(json_file, logger)

    for log in spec.logs.keys():
        print(log)


@click.command()
@click.argument("json_file")
@click.argument("message", required=False)
def dump_signal_list(json_file, message):
    logger = setup_logging()
    spec = get_spec(json_file, logger)

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
    logger = setup_logging()
    spec = get_spec(json_file, logger)

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
    logger = setup_logging()
    spec = get_spec(json_file, logger)

    print(spec.get_log(log))


@click.command()
@click.argument("json_file")
@click.argument("dev")
def print_dev(json_file, dev):
    logger = setup_logging()

    spec = get_spec(json_file, logger)

    print(spec.get_device(dev))


@click.command()
@click.argument("json_file")
@click.argument("message")
def print_msg(json_file, message):
    logger = setup_logging()
    spec = get_spec(json_file, logger)

    for dev in spec.devices.values():
        for name, msg in dev.msgs.items():
            if name == message:
                print(dev.name)
                print(msg)


@click.command()
@click.argument("json_file")
@click.argument("signal")
def print_signal(json_file, signal):
    logger = setup_logging()

    spec = get_spec(json_file, logger)

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
    """ Generate FCP documentation. 
    :param json_file: FCP json file path.
    :param out: output directory.
    """

    if link_location == None:
        link_location = "."

    logger = setup_logging()

    spec = get_spec(json_file, logger)
    generate_docs(spec, out, link_location, logger)

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
main.add_command(c_gen_cmd)
main.add_command(init_cmd)
main.add_command(validate_cmd)
main.add_command(gui_cmd)
main.add_command(dump_dev_list)
main.add_command(dump_msg_list)
main.add_command(dump_cfg_list)
main.add_command(dump_cmd_list)
main.add_command(dump_log_list)
main.add_command(dump_signal_list)
main.add_command(dump_signal_names)
main.add_command(print_log)
main.add_command(print_dev)
main.add_command(print_msg)
main.add_command(print_signal)
main.add_command(docs)

if __name__ == "__main__":
    main()



