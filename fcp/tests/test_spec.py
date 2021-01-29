from ..spec import *
import pytest

@pytest.fixture
def json():
    import json
    with open("../json/fst10e.json") as f:
        return json.loads(f.read())

def test_make_sid():
    assert make_sid(10, 10) == 330

def test_decompose_id():
    assert decompose_id(330) == (10,10)

def test_decompile(json):
    spec = Spec()
    spec.decompile(json)

def test_compile(json):
    spec = Spec()
    spec.decompile(json)
    j = spec.compile()

