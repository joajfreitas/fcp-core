"""Codegen handler."""

import importlib
import logging
import os
import pathlib
import pkgutil
import sys

from .result import Ok, Error

class CodeGenerator:
    """Base class for generators."""

    def __init__(self):
        pass

    def gen(self, fcp, templates, skels, output_path="output"):
        """Function called from fcp to trigger generator. Do not override."""

        self.verify(fcp).unwrap()

        output_path = pathlib.Path(output_path)
        os.makedirs(output_path, exist_ok=True)

        for path, content in self.generate(fcp, templates, skels).items():
            logging.info(output_path / path)
            with open(output_path / path, "w", encoding="utf-8") as file:
                file.write(content)

    def verify(self, fcp):
        if fcp is not None:
            return Ok(())
        else:
            return Error(["Received a None object instead of FcpV2"])

    def generate(self, fcp, templates, skel):
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

        return generators["fcp_" + generator_name].Generator()

    def generate(self, generator, template_dir, skel_dir, fcp):
        """Generate code"""
        generator = self.get_generator(generator)

        templates = {}
        for template in os.listdir(template_dir):
            template = pathlib.Path(template_dir) / pathlib.Path(template)
            with open(template, encoding="utf-8") as file:
                templates[template.stem] = file.read()

        skels = {}
        for skel in os.listdir(skel_dir):
            skel_path = pathlib.Path(skel_dir) / skel
            with open(skel_path, encoding="utf-8") as file:
                skels[skel] = file.read()

        generator.gen(fcp, templates, skels)
