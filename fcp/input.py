def to_type(str, f):
    if str == None:
        return None

    if str == "":
        return None

    return f(str)
