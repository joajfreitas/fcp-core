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
