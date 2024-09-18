"""Codegen handler."""

import importlib
import logging
import os
import pathlib
import pkgutil
import sys

from typing import Any, Union
from types import ModuleType


from .result import Ok, Error, Result, result_shortcut


class CodeGenerator:
    """Base class for generators."""

    def __init__(self) -> None:
        pass

    def gen(self, fcp: Result, templates: Any, skels: Any, output_path: str) -> None:
        """Function called from fcp to trigger generator. Do not override."""

        self.verify(fcp).unwrap()

        self.output_path = pathlib.Path(output_path)

        for path, content in self.generate(fcp, templates, skels).items():
            logging.info(f"Generating {path}")
            os.makedirs(path.parent, exist_ok=True)
            with open(path, "w", encoding="utf-8") as file:
                file.write(content)

    def verify(self, fcp: Any) -> Union[Ok, Error]:
        if fcp is not None:
            return Ok(())
        else:
            return Error(["Received a None object instead of FcpV2"])

    def generate(self, fcp: Any, templates: Any, skel: Any) -> Any:
        """Function to override from generator. Implements actual code generation."""
        return


class GeneratorManager:
    """Manager for generators"""

    def __init__(self) -> None:
        pass

    def list_generators(self) -> Any:
        """Find installed generators"""
        return [
            name for _, name, _ in pkgutil.iter_modules() if name.startswith("fcp_")
        ]

    def get_generator(self, generator_name: str) -> ModuleType:
        """Get generator by name."""
        generators = self.list_generators()
        if "fcp_" + generator_name not in generators:
            available_generators = [name[4:] for name in generators]
            logging.error("Code generator %s not available", generator_name)
            logging.info(
                "Currently available code generators: %s", available_generators
            )
            sys.exit(1)

        return importlib.import_module("fcp_" + generator_name)

    def get_templates(self, template_dir: str) -> Any:
        if template_dir is None:
            return {}

        templates = {}
        for template in os.listdir(template_dir):
            template_path = pathlib.Path(template_dir) / pathlib.Path(template)
            if not template_path.is_file():
                continue
            with open(template_path, encoding="utf-8") as file:
                templates[template_path.stem] = file.read()

        return templates

    def get_skels(self, skel_dir: str) -> Any:
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
    def generate(
        self,
        generator_name: str,
        template_dir: str,
        skel_dir: str,
        fcp: Any,
        sources: Any,
        output_path: str,
    ) -> Ok:
        """Generate code"""
        verifier = self.get_generator(generator_name).Verifier(sources)
        generator = self.get_generator(generator_name).Generator()

        verifier.verify(fcp).Q()

        templates = self.get_templates(template_dir)
        skels = self.get_skels(skel_dir)

        generator.gen(fcp, templates, skels, output_path)

        return Ok(())
