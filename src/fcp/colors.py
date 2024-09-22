from termcolor import colored


class Color:
    @staticmethod
    def red(s: str) -> str:
        return str(colored(s, "red"))

    @staticmethod
    def yellow(s: str) -> str:
        return str(colored(s, "yellow"))

    @staticmethod
    def orange(s: str) -> str:
        return str(colored(s, "light_red"))

    @staticmethod
    def blue(s: str) -> str:
        return str(colored(s, "blue"))

    @staticmethod
    def white(s: str) -> str:
        return str(colored(s, "white"))

    @staticmethod
    def boldred(s: str) -> str:
        return str(colored(s, "red", attrs=["bold"]))

    @staticmethod
    def boldyellow(s: str) -> str:
        return str(colored(s, "yellow", attrs=["bold"]))

    @staticmethod
    def boldorange(s: str) -> str:
        return str(colored(s, "light_red", attrs=["bold"]))

    @staticmethod
    def boldblue(s: str) -> str:
        return str(colored(s, "blue", attrs=["bold"]))

    @staticmethod
    def boldwhite(s: str) -> str:
        return str(colored(s, "white", attrs=["bold"]))
