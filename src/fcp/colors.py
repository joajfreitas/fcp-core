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

"""Colors."""

from termcolor import colored


class Color:
    """Color string with term codes."""

    @staticmethod
    def red(s: str) -> str:
        """Color string red."""
        return str(colored(s, "red"))

    @staticmethod
    def yellow(s: str) -> str:
        """Color string yellow."""
        return str(colored(s, "yellow"))

    @staticmethod
    def orange(s: str) -> str:
        """Color string orange."""
        return str(colored(s, "light_red"))

    @staticmethod
    def blue(s: str) -> str:
        """Color string blue."""
        return str(colored(s, "blue"))

    @staticmethod
    def white(s: str) -> str:
        """Color string white."""
        return str(colored(s, "white"))

    @staticmethod
    def boldred(s: str) -> str:
        """Color string bold red."""
        return str(colored(s, "red", attrs=["bold"]))

    @staticmethod
    def boldyellow(s: str) -> str:
        """Color string bold yellow."""
        return str(colored(s, "yellow", attrs=["bold"]))

    @staticmethod
    def boldorange(s: str) -> str:
        """Color string bold orange."""
        return str(colored(s, "light_red", attrs=["bold"]))

    @staticmethod
    def boldblue(s: str) -> str:
        """Color string bold blue."""
        return str(colored(s, "blue", attrs=["bold"]))

    @staticmethod
    def boldwhite(s: str) -> str:
        """Color string bold white."""
        return str(colored(s, "white", attrs=["bold"]))
