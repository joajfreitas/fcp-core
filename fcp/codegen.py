from v2_parser import get_fcp

import os
import pathlib
from jinja2 import Template
from pprint import pprint

class CodeGenerator:
    def __init__(self):
        pass
    
    def gen(self, fcp, templates):
        outputs = self.generate(fcp, templates)
        print(outputs)

    def generate(self, fcp):
        pass

class CGenerator(CodeGenerator):
    def __init__(self):
        pass
   
    def generate_module(self):
        return "module"

    def generate(self, fcp, templates):
        devices = [dev for dev in fcp.get_devices()]
        print(devices)
        print(templates["can_ids_h"].render(spec = {"common": {}}, devices = devices))
        fileset = []
        
        fileset.append(self.generate_module())
        return fileset


def main():
    fcp = get_fcp()
    generator = CGenerator()
    
    templates = {}
    for template in os.listdir("templates"):
        template = pathlib.Path("templates") / pathlib.Path(template)
        with open(template) as f:
            templates[template.stem] = Template(f.read())

    generator.gen(fcp, templates)

if __name__ == "__main__":
    main()
