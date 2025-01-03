"""Copyright (c) 2024 the fcp AUTHORS.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# ruff: noqa: D103 D100

import tempfile
import shutil
import subprocess
from pathlib import Path
from beartype.typing import List


class Source:
    """Interface for sources."""

    def apply(self, dirname: Path) -> str:
        """Commit the source to the target directory."""
        raise NotImplementedError


class File(Source):
    """Disk file source."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def apply(self, dirname: Path) -> str:
        """Commit the source to the target directory."""
        shutil.copy(self.path, dirname / self.path.name)

        return self.path.name


class InMemoryFile(Source):
    """In memory file source."""

    def __init__(self, name: str, contents: str):
        self.name = name
        self.contents = contents

    def apply(self, dirname: Path) -> str:
        """Commit the source to the target directory."""
        with open(dirname / self.name, "w") as f:
            f.write(self.contents)

        return self.name


def cc_binary(name: str, srcs: List[Source], headers: List[str]) -> None:
    """Build and run a C++ program."""
    src_paths = []

    tempdirname = tempfile.mkdtemp()

    for src in srcs:
        src_paths.append(src.apply(Path(tempdirname)))

    for header in headers:
        header.apply(Path(tempdirname))

    r = subprocess.run(
        ["/usr/bin/g++", "--std=c++17"] + src_paths + ["-o", name],
        capture_output=True,
        cwd=tempdirname,
    )

    if r.returncode != 0:
        print(r.stderr.decode())
        raise ValueError("Compilation failed")

    r = subprocess.run([Path(tempdirname) / name])
    if r.returncode != 0:
        print(r.stderr.decode())
        raise ValueError("Running executable failed")
