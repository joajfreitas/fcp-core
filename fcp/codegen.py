"""Codegen handler."""

import importlib
import logging
import os
import pathlib
import pkgutil
import sys
from functools import reduce

from .result import Ok, Error, result_shortcut
from .verifier import ErrorLogger


class CodeGenerator:
    """Base class for generators."""

    def __init__(self):
        pass

    def gen(self, fcp, templates, skels, output_path):
        """Function called from fcp to trigger generator. Do not override."""

        self.verify(fcp).unwrap()

        self.output_path = pathlib.Path(output_path)

        for path, content in self.generate(
            fcp, self.output_path, templates, skels
        ).items():
            logging.info(f"Generating {path}")
            os.makedirs(path.parent, exist_ok=True)
            with open(path, "w", encoding="utf-8") as file:
                file.write(content)

    def verify(self, fcp):
        if fcp is not None:
            return Ok(())
        else:
            return Error(["Received a None object instead of FcpV2"])

    def generate(self, fcp, output_path, templates, skel):
        """Function to override from generator. Implements actual code generation."""
        return


class GeneratorManager:
    """Manager for generators"""

    def __init__(self):
        pass

    def list_generators(self):
        """Find installed generators"""
        return {
            name: importlib.import_module(name)
            for finder, name, ispkg in pkgutil.iter_modules()
            if name.startswith("fcp_")
        }

    def get_generator(self, generator_name):
        """Get generator by name."""
        generators = self.list_generators()
        if "fcp_" + generator_name not in generators.keys():
            available_generators = [name[4:] for name in generators.keys()]
            logging.error("Code generator %s not available", generator_name)
            logging.info(
                "Currently available code generators: %s", available_generators
            )
            sys.exit(1)

        return generators["fcp_" + generator_name]

    def get_templates(self, template_dir):
        if template_dir is None:
            return {}

        templates = {}
        for template in os.listdir(template_dir):
            template = pathlib.Path(template_dir) / pathlib.Path(template)
            if not template.is_file():
                continue
            with open(template, encoding="utf-8") as file:
                templates[template.stem] = file.read()

        return templates

    def get_skels(self, skel_dir):
        if skel_dir is None:
            return {}

        skels = {}
        for skel in os.listdir(skel_dir):
            skel_path = pathlib.Path(skel_dir) / skel
            if not skel_path.is_file():
                continue
            with open(skel_path, encoding="utf-8") as file:
                skels[skel] = file.read()

        return skels

    @result_shortcut
    def generate(self, generator, template_dir, skel_dir, fcp, sources, output_path):
        """Generate code"""
        verifier = self.get_generator(generator).Verifier(sources)
        generator = self.get_generator(generator).Generator()

        verifier.verify(fcp).Q()

        templates = self.get_templates(template_dir)
        skels = self.get_skels(skel_dir)

        generator.gen(fcp, templates, skels, output_path)

        return Ok(())
