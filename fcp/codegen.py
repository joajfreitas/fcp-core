from .v2_parser import get_fcp

import os
import sys
import pathlib
import importlib
import pkgutil

from jinja2 import Template


class CodeGenerator:
    def __init__(self):
        pass

    def gen(self, fcp, templates, skels, output_path="output"):
        output_path = pathlib.Path(output_path)
        os.makedirs(output_path, exist_ok=True)

        for path, content in self.generate(fcp, templates, skels).items():
            print(output_path / path)
            with open(output_path / path, "w") as f:
                f.write(content)

    def generate(self, fcp, skel):
        pass




class GeneratorManager:
    def __init__(self):
        pass

    def list_generators(self):
        return {
            name: importlib.import_module(name)
            for finder, name, ispkg in pkgutil.iter_modules()
            if name.startswith("fcp_")
        }

    def generate(self, generator, template_dir, skel_dir, fcp):
        generators = self.list_generators()

        if "fcp_"+generator not in generators.keys():
            print(f"{generator} not available. Currently available code generators: {[name[4:] for name in generators.keys()]}")
            sys.exit(1)

        generator = generators["fcp_" + generator].Generator()

        templates = {}
        for template in os.listdir(template_dir):
            template = pathlib.Path(template_dir) / pathlib.Path(template)
            with open(template) as f:
                templates[template.stem] = f.read()

        skels = {}
        for skel in os.listdir(skel_dir):
            skel_path = pathlib.Path(skel_dir) / skel
            with open(skel_path) as f:
                skels[skel] = f.read()

        generator.gen(fcp, templates, skels)





if __name__ == "__main__":
    main()
