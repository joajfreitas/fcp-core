from typing import List

class Type:
    def get_length(self) -> int:
        raise NotImplemented()
    
    @staticmethod
    def get_default_types() -> List[str]:
        ints = ["i"+str(i) for i in range(1, 65)]
        uints = ["u"+str(i) for i in range(1, 65)]

        return ints + uints + ["f32", "f64"]

    @staticmethod
    def make_type( name):
        if name in Type.get_default_types():
            return DefaultType(name)
        else:
            raise NotImplemented()

class DefaultType(Type):
    def __init__(self, name):
        self.name = name
        self.length = int(name[1:])

    def get_length(self) -> int:
        return self.length
