from v2_parser import get_fcp

import os
import pathlib
import datetime
import itertools
import operator
from jinja2 import Template
from pprint import pprint


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


import importlib
import pkgutil

discovered_plugins = {
    name: importlib.import_module(name)
    for finder, name, ispkg
    in pkgutil.iter_modules()
    if name.startswith('fcp_')
}




def main():
    fcp = get_fcp()

    generator = discovered_plugins['fcp_cgen'].Generator()

    templates = {}
    for template in os.listdir("templates"):
        template = pathlib.Path("templates") / pathlib.Path(template)
        with open(template) as f:
            templates[template.stem] = Template(f.read())

    skels = {}
    for skel in os.listdir("skel"):
        skel_path = pathlib.Path("skel") / skel
        with open(skel_path) as f:
            skels[skel] = f.read()

    generator.gen(fcp, templates, skels)


if __name__ == "__main__":
    main()
