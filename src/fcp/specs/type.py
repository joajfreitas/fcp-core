from beartype.typing import List


class Type:
    def get_length(self) -> int:
        raise NotImplementedError()

    @staticmethod
    def get_default_types() -> List[str]:
        ints = ["i" + str(i) for i in range(1, 65)]
        uints = ["u" + str(i) for i in range(1, 65)]

        return ints + uints + ["f32", "f64"]

    @staticmethod
    def make_type(name: str) -> "Type":
        if name in Type.get_default_types():
            return DefaultType(name)
        else:
            raise NotImplementedError()


class DefaultType(Type):
    def __init__(self, name: str) -> None:
        self.name = name
        self.length = int(name[1:])

    def get_length(self) -> int:
        return self.length

class ArrayType(Type):
    def __init__(self, name: str, size: int) -> None:
        self.name = name
        self.size = size

class CompoundType(Type):
    def __init__(self, name: str) -> None:
        self.name = name
