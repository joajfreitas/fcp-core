from fcp import Spec, Enum
import json


class TestSpec:
    def get_json1(self):
        return """{
    "devices" : {
        "ccu_right": {
            "name": "ccu_right",
            "id": 25,
            "msgs": {},
            "cmds": {},
            "cfgs": {}
        }
    },
    "common": {
        "name": "common",
        "id": 0,
        "msgs": {}
    },
    "logs" : {
        "wrong_log_id" : {
            "id": 0,
            "name": "wrong_log_id",
            "n_args": 0,
            "comment": "",
            "string": "Log code was not found"
        }

    },
    "version": "0.2"
}
"""

    def test_spec_device(self):
        spec = Spec()
        spec.decompile(json.loads(self.get_json1()))
        
        assert spec.devices["ccu_right"].name == "ccu_right"
        assert spec.devices["ccu_right"].id == 25
        assert spec.devices["ccu_right"].msgs == {}
        assert spec.devices["ccu_right"].cmds == {}
        assert spec.devices["ccu_right"].cfgs == {}

    def test_spec_logs(self):
        spec = Spec()
        spec.decompile(json.loads(self.get_json1()))
        
        assert spec.logs["wrong_log_id"].name == "wrong_log_id"
        assert spec.logs["wrong_log_id"].id == 0
        assert spec.logs["wrong_log_id"].n_args == 0
        assert spec.logs["wrong_log_id"].comment == ""
        assert spec.logs["wrong_log_id"].string == "Log code was not found"

    def test_spec_common(self):
        spec = Spec()
        spec.decompile(json.loads(self.get_json1()))
        
        assert spec.common.name == "common"
        assert spec.common.id == 0
        assert spec.common.msgs == {}
    
    def test_spec_enum_compile(self):
        enum = Enum()
        enum.name = "enum1"
        enum.enumeration = {"value1": 0, "value2": 1, "value3": 2}
        d = enum.compile()

        assert d["name"] == "enum1"
        assert d["enumeration"]["value1"] == 0
        assert d["enumeration"]["value2"] == 1
        assert d["enumeration"]["value3"] == 2

    def test_spec_enum_decompile(self):
        enum_json = """ 
{
    "name": "enum1",
    "enumeration": {
        "value1": 0,
        "value2": 1,
        "value3": 2
     }
}
"""
        
        j = json.loads(enum_json) 
        enum = Enum()
        enum.decompile(j)

        assert enum.name == "enum1"
        assert enum.enumeration["value1"] == 0
        assert enum.enumeration["value2"] == 1
        assert enum.enumeration["value3"] == 2
        
