import pytest
import json

from ..dbc_reader import read_dbc

@pytest.fixture
def dbc():
    with open("dbc/FST09e.dbc") as f:
        return f.read()

@pytest.fixture
def device_config():
    with open("json/device_config.json") as f:
        return json.loads(f.read())

def test_read_dbc():
    read_dbc("dbc/FST09e.dbc", "test.json", "json/device_config.json")





