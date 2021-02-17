from typing import *

def normalize(xs: Dict[str, Any], key: Callable[[Any], str] = None):
    """Update xs dictionary keys according to key.
        By default key is `lambda x : x.name`

    :param xs: Dictionary containing spec node
    :param key: Function that returns the key for a particular node
    """

    if key == None:
        key = lambda x: x.name

    aux = []

    for k, x in xs.items():
        if k != key(x):
            aux.append((k, key(x)))

    for k, key in aux:
        xs[key] = xs[k]
        del xs[k]
