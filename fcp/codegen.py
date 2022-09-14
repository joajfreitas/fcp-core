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


class CodeVerifier:
    """Base class for verifiers"""

    def __init__(self, sources):
        self.error_logger = ErrorLogger(sources)
        pass

    def apply_check(self, category, value):
        result = Ok(())
        for name, f in self.__class__.__dict__.items():
            if name.startswith(f"check_{category}"):
                result = result.compound(f(self, value))

        return result

    def apply_checks(self, category, values):
        results = list(map(lambda value: self.apply_check(category, value), values))
        return reduce(lambda x, y: x.compound(y), results)

    def verify(self, fcp_v2):
        logging.info("Running verifier")

        result = Ok(())

        result = result.compound(self.apply_check("fcp_v2", fcp_v2))
        result = result.compound(self.apply_checks("enum", fcp_v2.enums))
        result = result.compound(self.apply_checks("struct", fcp_v2.structs))
        result = result.compound(self.apply_checks("broadcast", fcp_v2.broadcasts))

        for struct in fcp_v2.structs:
            result = result.compound(self.apply_checks("signal", struct.signals))

        return result


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

        return generators["fcp_" + generator_name]

    @result_shortcut
    def generate(self, generator, template_dir, skel_dir, fcp, sources):
        """Generate code"""
        verifier = self.get_generator(generator).Verifier(sources)
        generator = self.get_generator(generator).Generator()

        verifier.verify(fcp).Q()

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
