#!/usr/bin/env python3

"""c-generator.

Usage:
  c-generator.py generate <json> <template> <skel> <output>
  c-generator.py (-h | --help)
  c-generator.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import sys, os
import json

import logging
import shutil

from .spec import Spec
from .template import Tpl
from .generator import *
from .validator import validate


def check_output(output):
    if not os.path.isdir(output):
        try:
            os.makedirs(output)
        except Exception as e:
            return False, str(e)

    return True, ""


def write_files(output, can_ids, devices, common):
    def gen_output(d):
        return os.path.join(output, d)

    can_ids_c, can_ids_h = can_ids
    can_ids_path = gen_output("can_ids.h")
    with open(can_ids_path, "w") as f:
        f.write(can_ids_h)

    can_ids_path = gen_output("can_ids.c")
    with open(can_ids_path, "w") as f:
        f.write(can_ids_c)

    common_c, common_h = common
    common_c_path = gen_output("common.c")
    with open(common_c_path, "w") as f:
        f.write(common_c)

    common_h_path = gen_output("common.h")
    with open(common_h_path, "w") as f:
        f.write(common_h)

    for name, h, c in devices:
        c_path = gen_output(name + "_can.c")
        h_path = gen_output(name + "_can.h")

        with open(c_path, "w") as f:
            f.write(c)

        with open(h_path, "w") as f:
            f.write(h)


def check_version(j, logger):
    version = j.get("version")

    if version == None:
        logger.error("No version found")
        exit()

    if version != "0.2":
        logger.error("Wrong file version expected 0.2")
        exit()

    logger.info("Correct file version ✅")


def c_gen(templates, output, json_file, skel, logger):
    # copy skel directory
    status, err = check_output(output)
    for file in os.listdir(skel):
        shutil.copy(os.path.join(skel, file), output, follow_symlinks=True)

    if not status:
        logger.error(err)
        exit()

    tpl = Tpl(templates)
    status, err = tpl.check_tpl_dir()
    if not status:
        logger.error(err)
        exit()

    logger.info("Template dir checked ✅")

    tpl.open_tpl_files()

    with open(json_file) as f:
        r = f.read()

    logger.info("JSON spec file successfully read ✅")

    j = json.loads(r)
    ans = validate(logger, j)
    if not ans:
        return
    logger.info("Validated JSON ✅")
    spec = Spec()
    spec.decompile(j)

    check_version(j, logger)

    logger.info("JSON loaded into Spec ✅")

    can_ids = build_can_ids(spec, tpl)

    devices = [build_devices(spec, device, tpl) for device in spec.devices.values()]

    common = build_common(spec, tpl)

    write_files(output, can_ids, devices, common)
