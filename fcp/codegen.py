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


class CGenerator(CodeGenerator):
    def __init__(self):
        pass

    def config(self, fcp):
        types = {struct.name: struct for struct in fcp.structs}
        types.update({enum.name: enum for enum in fcp.enums})

        devices = {}

        for device in fcp.devices:
            devices[device.name] = {
                "name": device.name,
                "signature": f"dev_{device.name}_t",
                "id": int(device.id),
                "msgs": {},
                "cfgs": {},
                "cmds": {},
            }
            for broadcast in fcp.broadcasts:
                if broadcast.data["device"].data["value"] == device.name:
                    dev_id = devices[device.name]["id"]
                    sid = int(broadcast.data["id"].data["value"])
                    msg_id = int((sid - dev_id) / 32)

                    struct = types[broadcast.data["type"].data["value"]]

                    lengths = list([int(signal["params"][0][1:]) for signal in struct.data["fields"]])
                    starts = list(itertools.accumulate([0] + lengths, operator.add))[:-1]
                    
                    msg = {
                        "name": broadcast.name,
                        "id": msg_id,
                        "dlc": broadcast.data["dlc"].data["value"],
                        "type": f"{broadcast.name}_t",
                        "signals": {
                            signal["name"]: {
                                "mux_count": 0,
                                "name": signal["name"],
                                "type": "unsigned",
                                "dst_type": "uint16_t",
                                "length": lengths[i],
                                "start": starts[i],
                                "scale": 1.0,
                                "offset": 0.0,
                            }
                            for i, signal in enumerate(struct.data["fields"])
                        },
                    }
                    devices[device.name]["msgs"][broadcast.name] = msg

        return {
            "signature": "can_t",
            "devices": devices,
            "common": {"signature": "dev_common_t", "name": "common", "msgs": {}},
        }

    def generate_can_ids_h(self, template, spec):
        return template.render(
            date=datetime.datetime.now(),
            spec=spec,
            logs=[],
        )

    def generate_can_ids_c(self, template, spec):
        return template.render(date=datetime.datetime.now(), spec=spec)

    def generate_common_c(self, template, spec):
        return template.render(date=datetime.datetime.now(), spec=spec)

    def generate_common_h(self, template, spec):
        return template.render(
            date=datetime.datetime.now(),
            spec=spec,
        )

    def generate_c(self, template, device):
        return template.render(
            date=datetime.datetime.now(),
            device=device,
        )

    def generate_h(self, template, device):
        return template.render(
            date=datetime.datetime.now(),
            device=device,
        )

    def generate(self, fcp, templates={}, skels={}):
        spec = self.config(fcp)
        fileset = {
            "can_ids.h": self.generate_can_ids_h(templates.get("can_ids_h"), spec),
            "can_ids.c": self.generate_can_ids_c(templates.get("can_ids_c"), spec),
            "common.c": self.generate_common_c(templates.get("common_c"), spec),
            "common.h": self.generate_common_h(templates.get("common_h"), spec),
            "candata.h": skels["candata.h"],
            "signal_parser.c": skels["signal_parser.c"],
            "signal_parser.h": skels["signal_parser.h"],
        }

        for dev in fcp.get_devices():
            device = spec["devices"][dev.name]
            fileset[f"{dev.name}_can.c"] = self.generate_c(templates.get("c"), device)
            fileset[f"{dev.name}_can.h"] = self.generate_h(templates.get("h"), device)

        return fileset


def main():
    fcp = get_fcp()
    generator = CGenerator()

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
