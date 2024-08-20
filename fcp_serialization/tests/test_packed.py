import pytest

#from ..fcp_serialization import packed
#from fcp import FcpV2, Enum, Enumeration, Struct, Signal, Broadcast


#@pytest.fixture
#def fcp_v2():
#    return FcpV2(
#        devices=[],
#        structs=[
#            Struct("base1", signals=[Signal("s1", 0, "u16"), Signal("s2", 1, "u32")])
#        ],
#        broadcasts=[],
#        enums=[],
#        logs=[],
#    )
#
#
#@pytest.mark.parametrize(
#    "type, size",
#    [
#        ("u1", 1),
#        ("u2", 2),
#        ("u3", 3),
#        ("u8", 8),
#        ("u16", 16),
#        ("u32", 32),
#        ("u64", 64),
#        ("i1", 1),
#        ("i8", 8),
#        ("i16", 16),
#        ("i32", 32),
#        ("i64", 64),
#        ("f32", 32),
#        ("f64", 64),
#        (Enum("test", [Enumeration("value1", 0)]), 1),
#        (Enum("test", [Enumeration("value1", 1)]), 1),
#        (Enum("test", [Enumeration("v1", 1), Enumeration("v2", 2)]), 2),
#        (Enum("test", [Enumeration("v1", 1), Enumeration("v2", 4095)]), 12),
#        (Struct("test", signals=[]), 0),
#        (
#            Struct("test", signals=[Signal("s1", 0, "u16"), Signal("s2", 0, "base1")]),
#            64,
#        ),
#    ],
#)
#def test_type_size(fcp_v2, type, size):
#    assert packed.get_size(fcp_v2, type) == size
#
#
#@pytest.mark.parametrize(
#    "structs, type, allocation",
#    [
#        ([], "base1", [("s1", 0, 16), ("s2", 16, 32)]),
#        (
#            [
#                Struct("S1", [Signal("s1", 0, "u16"), Signal("s2", 1, "u16")]),
#                Struct("S2", [Signal("s1", 0, "S1")]),
#            ],
#            "S2",
#            [("s1", 0, 32)],
#        ),
#        (
#            [
#                Struct(
#                    "S1",
#                    [
#                        Signal("s1", 0, "u1"),
#                        Signal("s2", 1, "S2"),
#                        Signal("s3", 2, "S3"),
#                    ],
#                ),
#                Struct("S2", [Signal("s1", 0, "u8")]),
#                Struct("S3", [Signal("s1", 0, "u32")]),
#            ],
#            "S1",
#            [("s1", 0, 1), ("s2", 1, 8), ("s3", 9, 32)],
#        ),
#    ],
#)
#def test_allocate_message(fcp_v2, structs, type, allocation):
#    fcp_v2.structs += structs
#
#    assert (
#        list(packed.allocate_message(fcp_v2, Broadcast("B1", {"type": type}, [])))
#        == allocation
#    )
