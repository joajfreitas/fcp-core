"""Codegen."""

# Copyright (c) 2024 the fcp AUTHORS.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import importlib
import logging
import os
import pathlib
import pkgutil
import sys
from pathlib import Path

from beartype.typing import Any, Dict, Union, NoReturn, List
from types import ModuleType

from .types import Nil, Never
from .result import Result, Ok
from .maybe import catch
from . import FcpV2
from .verifier import Verifier


<<<<<<< HEAD
def _handle_file(result: Dict[str, Union[str, Path]]) -> NoReturn:
=======
def handle_file(result: Dict[str, Union[str, Path]]) -> None:
>>>>>>> fa5111d (C structs and decode macros being generated)
    path: Path = Path(result.get("path"))  # type: ignore
    logging.info(f"Generating {path}")

    path.parent.mkdir(exist_ok=True)
    path.write_text(str(result.get("contents")))


<<<<<<< HEAD
def _handle_print(result: Dict[str, Union[str, Path]]) -> NoReturn:
    print(result.get("contents"))


def handle_result(result: Dict[str, Union[str, Path]]) -> NoReturn:
    """Handle results from plugins."""
=======
def handle_print(result: Dict[str, Union[str, Path]]) -> None:
    print(result.get("contents"))


def handle_result(result: Dict[str, Union[str, Path]]) -> None:
>>>>>>> fa5111d (C structs and decode macros being generated)
    if result.get("type") == "file":
        _handle_file(result)
    elif result.get("type") == "print":
        _handle_print(result)
    else:
        logging.error(f"Cannot handle result of type: {result.get('type')}")


class CodeGenerator:
    """Base class for generators."""

    def __init__(self) -> None:
        pass

    def gen(self, fcp: FcpV2, templates: Any, skels: Any, output_path: str) -> None:
        """Function called from fcp to trigger generator. Do not override."""
        self.output_path = pathlib.Path(output_path)

        ctx = {
            "templates": templates,
            "skels": skels,
            "output": self.output_path,
        }

        for result in self.generate(fcp, ctx):
            handle_result(result)

<<<<<<< HEAD
    def generate(self, fcp: FcpV2, ctx: Any) -> Dict[str, Union[str, Path]]:
=======
    def verify(self, fcp: Any, verifier: Verifier) -> Result[Nil, str]:
        self.register_checks(verifier)

        return verifier.verify(fcp)

    def generate(self, fcp: FcpV2, ctx: Any) -> List[Dict[str, Union[str, Path]]]:
>>>>>>> fa5111d (C structs and decode macros being generated)
        """Function to override from generator. Implements actual code generation."""
        raise NotImplementedError

<<<<<<< HEAD
    def register_checks(self, verifier: Verifier) -> Never:  # type: ignore
        """Register checks in verifier."""
=======
    def register_checks(self, verifier: Verifier) -> None:  # type: ignore
>>>>>>> fa5111d (C structs and decode macros being generated)
        pass


class GeneratorManager:
    """Manager for generators."""

    def __init__(self, verifier: Verifier) -> None:
        self.verifier = verifier

    def _list_generators(self) -> Any:
        return [
            name for _, name, _ in pkgutil.iter_modules() if name.startswith("fcp_")
        ]

    def _get_generator(self, generator_name: str) -> ModuleType:
        generators = self._list_generators()
        if "fcp_" + generator_name not in generators:
            available_generators = [name[4:] for name in generators]
            logging.error("Code generator %s not available", generator_name)
            logging.info(
                "Currently available code generators: %s", available_generators
            )
            sys.exit(1)

        return importlib.import_module("fcp_" + generator_name)

    def _get_templates(self, template_dir: str) -> Any:
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

    def _get_skels(self, skel_dir: str) -> Any:
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

    @catch
    def generate(
        self,
        generator_name: str,
        template_dir: str,
        skel_dir: str,
        fcp: Any,
        sources: Any,
        output_path: str,
    ) -> Result[Nil, str]:
        """Generate code."""
        generator = self._get_generator(generator_name).Generator()
        generator.register_checks(self.verifier)
        self.verifier.verify(fcp).attempt()

        templates = self._get_templates(template_dir)
        skels = self._get_skels(skel_dir)

        generator.gen(fcp, templates, skels, output_path)

        return Ok(())