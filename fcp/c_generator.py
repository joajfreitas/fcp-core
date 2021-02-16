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

from .specs import Spec
from .template import Tpl
from .generator import *


def check_output(output):
    if not os.path.isdir(output):
        try:
            os.makedirs(output)
        except Exception as e:
            return False, str(e)

    return True, ""


def write_files(output, files):
    def gen_output(d):
        return os.path.join(output, d)

    for name, content in files:
        if content == "":
            continue
        with open(gen_output(name), "w") as f:
            f.write(content)


def check_version(j, logger):
    version = j.get("version")

    if version == None:
        logger.error("No version found")
        exit()

    if version != "0.2":
        logger.error("Wrong file version expected 0.2")
        exit()

    logger.info("Correct file version ✅")


def c_gen(spec, templates, output, skel, logger):
    # copy skel directory
    status, err = check_output(output)
    if not status:
        logger.error(err)
        exit()

    for file in os.listdir(skel):
        shutil.copy(os.path.join(skel, file), output, follow_symlinks=True)

    tpl = Tpl(logger, templates)
    status, err = tpl.check_tpl_dir()
    if not status:
        logger.error(err)

    logger.info("Template dir checked ✅")

    tpl.open_tpl_files()

    files = []

    can_ids = build_can_ids(spec, tpl)
    for device in spec.devices.values():
        files += build_devices(spec, device, tpl)

    common = build_common(spec, tpl)
    enums = build_enums(spec, tpl)

    files += can_ids + common + enums

    write_files(output, files)
