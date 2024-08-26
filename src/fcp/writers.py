from pathlib import Path
from typing import Any

# TODO: replace any type hints with a more specific type


class FpiWriter:
    def __init__(self, output_path: str) -> None:
        self.output_path = Path(output_path)

    def write_main(self, nodes: dict[str, Any]) -> str:
        return "\n".join([f"import {name};" for name in nodes.keys()])

    def write(self, fpis: dict[str, Any]) -> None:
        for filename, nodes in fpis.items():
            with open(self.output_path / (filename + ".fpi"), "w") as f:
                f.write('version: "3"\n\n')
                f.write("\n\n".join(nodes))

            with open(self.output_path / "main.fpi", "w") as f:
                f.write('version: "3"\n\n')
                f.write(self.write_main(fpis))


class FcpWriter:
    def __init__(self, output_path: str) -> None:
        self.output_path = Path(output_path)

    def write_main(self, nodes: dict[str, Any]) -> str:
        return "\n".join([f"import {name};" for name in nodes.keys()])

    def write(self, fcps: dict[str, Any]) -> None:
        for filename, nodes in fcps.items():
            with open(self.output_path / (filename + ".fcp"), "w") as f:
                f.write('version: "3"\n\n')
                f.write("\n\n".join(nodes))

            with open(self.output_path / "main.fcp", "w") as f:
                f.write('version: "3"\n\n')
                f.write(self.write_main(fcps))
