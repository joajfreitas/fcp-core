import sys
import json
from spec import Spec, Device

from input import to_type


def main(args):
    with open(args[1]) as f:
        j = json.loads(f.read())

    spec = Spec(j)

    d = Device()

    name = input("Device name: ")
    d.name = to_type(name, str)
    id = input("Device id: ")
    d.id = to_type(id, int)
    spec.add_device(d.compile())

    with open(args[1], "w") as f:
        f.write(json.dumps(spec.json, sort_keys=True, indent=4))


if __name__ == "__main__":
    main(sys.argv)
