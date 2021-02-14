from ..specs import *
import pytest

@pytest.fixture
def json():
    import json
    with open("json/test.json") as f:
        return json.loads(f.read())

@pytest.fixture
def spec(json):
    spec = Spec()
    spec.decompile(json)
    return spec



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

