class ParamInt:
    def __init__(self):
        pass

    def parse(self, value):
        return int(value[0])


class ParamFloat:
    def __init__(self):
        pass

    def parse(self, value):
        return float(value[0])


class ParamStr:
    def __init__(self):
        pass

    def parse(self, value):
        return value[0][1:-1]


class ParamParam:
    def __init__(self, name, *args):
        self.name = name
        self.args = args

    def parse(self, value):
        for arg in self.args:
            yield arg.parse(value)


class Param:
    @staticmethod
    def Param(name, *args):
        return ParamParam(name, *args)

    @staticmethod
    def Int():
        return ParamInt()

    @staticmethod
    def Float():
        return ParamFloat()

    @staticmethod
    def Str():
        return ParamStr()


class ParamParser:
    def __init__(self, *params):
        self.params = {}
        for param in params:
            self.params[param.name] = param

    def parse(self, params):
        for key, value in params.items():
            print(list(self.params[key].parse(value)))


parser = ParamParser(
    Param.Param("id", Param.Int()),
    Param.Param("device", Param.Str()),
    Param.Param("start", Param.Int()),
    Param.Param("length", Param.Int()),
    Param.Param("sat", Param.Float(), Param.Float()),
)

parser.parse({"device": ('"pdu"',), "id": ("11",)})
parser.parse({"start": ("0",), "length": ("16",), "sat": ("0.0", "1.0")})

params_spec = {
    "id": Param.Param(Param.Int()),
    "dlc": {"type": int},
    "start": {"type": int},
    "length": {"type": int},
    "scale": {"type": float},
    "offset": {"type": float},
    "min_value": {"type": float},
    "max_value": {"type": float},
    "n_args": {"type": int},
    "mux_count": {"type": int},
}
