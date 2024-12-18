#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "generated_code/can_frame.h"
#include "generated_code/ecu_can.h"

bool all_tests_passed = true;

typedef union {
    float f;
    uint32_t i;
} F32;

typedef union {
    double d;
    uint64_t i;
} F64;

#define VERIFY_TEST(condition)                             \
    if (condition) {                                       \
        printf("\033[32m [PASSED] %s\n", __func__);        \
    } else {                                               \
        printf("\033[31m [FAILED] %s\033[0m\n", __func__); \
        all_tests_passed = false;                          \
    }

#define ASSERT_TESTS()      \
    printf("\033[0m");      \
    if (all_tests_passed) { \
        exit(EXIT_SUCCESS); \
    } else {                \
        exit(EXIT_FAILURE); \
    }

bool compare_frames(CanFrame *a, CanFrame *b) {
    if (a->id != b->id) {
        return false;
    }

    if (a->dlc != b->dlc) {
        return false;
    }

    for (int i = 0; i < a->dlc; i++) {
        if (a->data[i] != b->data[i]) {
            return false;
        }
    }

    return true;
}

// Test functions for all types
void test_encode_msg_u8s(CanFrame *f) {
    CanFrame expected = {
        .id = CAN_MSG_ID_U8_S,
        .data = {0x12, 0, 0, 0, 0, 0, 0, 0},
        .dlc = 1,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_u8s(CanMsgU8S *original, CanFrame *f) {
    CanMsgU8S decoded = can_decode_msg_u8_s(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_u16s(CanFrame *f) {
    CanFrame expected = {
        .id = CAN_MSG_ID_U16_S,
        .data = {0x34, 0x12, 0, 0, 0, 0, 0, 0},
        .dlc = 2,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_u16s(CanMsgU16S *original, CanFrame *f) {
    CanMsgU16S decoded = can_decode_msg_u16_s(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_u32s(CanFrame *f) {
    CanFrame expected = {
        .id = CAN_MSG_ID_U32_S,
        .data = {0x78, 0x56, 0x34, 0x12, 0, 0, 0, 0},
        .dlc = 4,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_u32s(CanMsgU32S *original, CanFrame *f) {
    CanMsgU32S decoded = can_decode_msg_u32_s(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_u64s(CanFrame *f) {
    CanFrame expected = {
        .id = CAN_MSG_ID_U64_S,
        .data = {0xF0, 0xDE, 0xBC, 0x9A, 0x78, 0x56, 0x34, 0x12},
        .dlc = 8,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_u64s(CanMsgU64S *original, CanFrame *f) {
    CanMsgU64S decoded = can_decode_msg_u64_s(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_i8s(CanFrame *f) {
    CanFrame expected = {
        .id = CAN_MSG_ID_I8_S,
        .data = {0x12, 0, 0, 0, 0, 0, 0, 0},
        .dlc = 1,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_i8s(CanMsgI8S *original, CanFrame *f) {
    CanMsgI8S decoded = can_decode_msg_i8_s(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_i16s(CanFrame *f) {
    CanFrame expected = {
        .id = CAN_MSG_ID_I16_S,
        .data = {0x34, 0x12, 0, 0, 0, 0, 0, 0},
        .dlc = 2,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_i16s(CanMsgI16S *original, CanFrame *f) {
    CanMsgI16S decoded = can_decode_msg_i16_s(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_i32s(CanFrame *f) {
    CanFrame expected = {
        .id = CAN_MSG_ID_I32_S,
        .data = {0x78, 0x56, 0x34, 0x12, 0, 0, 0, 0},
        .dlc = 4,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_i32s(CanMsgI32S *original, CanFrame *f) {
    CanMsgI32S decoded = can_decode_msg_i32_s(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_i64s(CanFrame *f) {
    CanFrame expected = {
        .id = CAN_MSG_ID_I64_S,
        .data = {0xF0, 0xDE, 0xBC, 0x9A, 0x78, 0x56, 0x34, 0x12},
        .dlc = 8,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_i64s(CanMsgI64S *original, CanFrame *f) {
    CanMsgI64S decoded = can_decode_msg_i64_s(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_f32s(CanFrame *f) {
    F32 v = {.f = 5.843f};

    CanFrame expected = {
        .id = CAN_MSG_ID_F32_S,
        .data = {v.i, v.i >> 8, v.i >> 16, v.i >> 24, 0, 0, 0, 0},
        .dlc = 4,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_f32s(CanMsgF32S *original, CanFrame *f) {
    CanMsgF32S decoded = can_decode_msg_f32_s(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_f64s(CanFrame *f) {
    F64 v = {.d = 5.84367431557};

    CanFrame expected = {
        .id = CAN_MSG_ID_F64_S,
        .data = {v.i, v.i >> 8, v.i >> 16, v.i >> 24, v.i >> 32, v.i >> 40, v.i >> 48, v.i >> 56},
        .dlc = 8,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_f64s(CanMsgF64S *original, CanFrame *f) {
    CanMsgF64S decoded = can_decode_msg_f64_s(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_u8b(CanFrame *f) {
    CanFrame expected = {
        .id = CAN_MSG_ID_U8_B,
        .data = {0x12, 0, 0, 0, 0, 0, 0, 0},
        .dlc = 1,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_u8b(CanMsgU8B *original, CanFrame *f) {
    CanMsgU8B decoded = can_decode_msg_u8_b(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_u16b(CanFrame *f) {
    CanFrame expected = {
        .id = CAN_MSG_ID_U16_B,
        .data = {0x12, 0x34, 0, 0, 0, 0, 0, 0},
        .dlc = 2,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_u16b(CanMsgU16B *original, CanFrame *f) {
    CanMsgU16B decoded = can_decode_msg_u16_b(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_u32b(CanFrame *f) {
    CanFrame expected = {
        .id = CAN_MSG_ID_U32_B,
        .data = {0x12, 0x34, 0x56, 0x78, 0, 0, 0, 0},
        .dlc = 4,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_u32b(CanMsgU32B *original, CanFrame *f) {
    CanMsgU32B decoded = can_decode_msg_u32_b(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_u64b(CanFrame *f) {
    CanFrame expected = {
        .id = CAN_MSG_ID_U64_B,
        .data = {0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0},
        .dlc = 8,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_u64b(CanMsgU64B *original, CanFrame *f) {
    CanMsgU64B decoded = can_decode_msg_u64_b(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_i8b(CanFrame *f) {
    CanFrame expected = {
        .id = CAN_MSG_ID_I8_B,
        .data = {0x12, 0, 0, 0, 0, 0, 0, 0},
        .dlc = 1,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_i8b(CanMsgI8B *original, CanFrame *f) {
    CanMsgI8B decoded = can_decode_msg_i8_b(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_i16b(CanFrame *f) {
    CanFrame expected = {
        .id = CAN_MSG_ID_I16_B,
        .data = {0x12, 0x34, 0, 0, 0, 0, 0, 0},
        .dlc = 2,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_i16b(CanMsgI16B *original, CanFrame *f) {
    CanMsgI16B decoded = can_decode_msg_i16_b(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_i32b(CanFrame *f) {
    CanFrame expected = {
        .id = CAN_MSG_ID_I32_B,
        .data = {0x12, 0x34, 0x56, 0x78, 0, 0, 0, 0},
        .dlc = 4,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_i32b(CanMsgI32B *original, CanFrame *f) {
    CanMsgI32B decoded = can_decode_msg_i32_b(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_i64b(CanFrame *f) {
    CanFrame expected = {
        .id = CAN_MSG_ID_I64_B,
        .data = {0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0},
        .dlc = 8,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_i64b(CanMsgI64B *original, CanFrame *f) {
    CanMsgI64B decoded = can_decode_msg_i64_b(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_f32b(CanFrame *f) {
    F32 v = {.f = 7.45f};

    CanFrame expected = {
        .id = CAN_MSG_ID_F32_B,
        .data = {v.i >> 24, v.i >> 16, v.i >> 8, v.i, 0, 0, 0, 0},
        .dlc = 4,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_f32b(CanMsgF32B *original, CanFrame *f) {
    CanMsgF32B decoded = can_decode_msg_f32_b(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_f64b(CanFrame *f) {
    F64 v = {.d = 7.4572418329};

    CanFrame expected = {
        .id = CAN_MSG_ID_F64_B,
        .data = {v.i >> 56, v.i >> 48, v.i >> 40, v.i >> 32, v.i >> 24, v.i >> 16, v.i >> 8, v.i},
        .dlc = 8,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_f64b(CanMsgF64B *original, CanFrame *f) {
    CanMsgF64B decoded = can_decode_msg_f64_b(f);

    VERIFY_TEST(original->val == decoded.val);
}

int main() {
    printf("Running Tests...\n\n");

    CanMsgU8S msg_u8s = {.val = 0x12};
    CanMsgU16S msg_u16s = {.val = 0x1234};
    CanMsgU32S msg_u32s = {.val = 0x12345678};
    CanMsgU64S msg_u64s = {.val = 0x123456789abcdef0};
    CanMsgI8S msg_i8s = {.val = 0x12};
    CanMsgI16S msg_i16s = {.val = 0x1234};
    CanMsgI32S msg_i32s = {.val = 0x12345678};
    CanMsgI64S msg_i64s = {.val = 0x123456789abcdef0};
    CanMsgF32S msg_f32s = {.val = 5.843};
    CanMsgF64S msg_f64s = {.val = 5.84367431557};

    CanFrame frame_u8s = can_encode_msg_u8_s(&msg_u8s);
    CanFrame frame_u16s = can_encode_msg_u16_s(&msg_u16s);
    CanFrame frame_u32s = can_encode_msg_u32_s(&msg_u32s);
    CanFrame frame_u64s = can_encode_msg_u64_s(&msg_u64s);
    CanFrame frame_i8s = can_encode_msg_i8_s(&msg_i8s);
    CanFrame frame_i16s = can_encode_msg_i16_s(&msg_i16s);
    CanFrame frame_i32s = can_encode_msg_i32_s(&msg_i32s);
    CanFrame frame_i64s = can_encode_msg_i64_s(&msg_i64s);
    CanFrame frame_f32s = can_encode_msg_f32_s(&msg_f32s);
    CanFrame frame_f64s = can_encode_msg_f64_s(&msg_f64s);

    CanMsgU8B msg_u8b = {.val = 0x12};
    CanMsgU16B msg_u16b = {.val = 0x1234};
    CanMsgU32B msg_u32b = {.val = 0x12345678};
    CanMsgU64B msg_u64b = {.val = 0x123456789abcdef0};
    CanMsgI8B msg_i8b = {.val = 0x12};
    CanMsgI16B msg_i16b = {.val = 0x1234};
    CanMsgI32B msg_i32b = {.val = 0x12345678};
    CanMsgI64B msg_i64b = {.val = 0x123456789abcdef0};
    CanMsgF32B msg_f32b = {.val = 7.45};
    CanMsgF64B msg_f64b = {.val = 7.4572418329};

    CanFrame frame_u8b = can_encode_msg_u8_b(&msg_u8b);
    CanFrame frame_u16b = can_encode_msg_u16_b(&msg_u16b);
    CanFrame frame_u32b = can_encode_msg_u32_b(&msg_u32b);
    CanFrame frame_u64b = can_encode_msg_u64_b(&msg_u64b);
    CanFrame frame_i8b = can_encode_msg_i8_b(&msg_i8b);
    CanFrame frame_i16b = can_encode_msg_i16_b(&msg_i16b);
    CanFrame frame_i32b = can_encode_msg_i32_b(&msg_i32b);
    CanFrame frame_i64b = can_encode_msg_i64_b(&msg_i64b);
    CanFrame frame_f32b = can_encode_msg_f32_b(&msg_f32b);
    CanFrame frame_f64b = can_encode_msg_f64_b(&msg_f64b);

    printf("\033[34m\nRunning Encoding Tests on Little Endian...\033[0m\n\n");

    test_encode_msg_u8s(&frame_u8s);
    test_encode_msg_u16s(&frame_u16s);
    test_encode_msg_u32s(&frame_u32s);
    test_encode_msg_u64s(&frame_u64s);
    test_encode_msg_i8s(&frame_i8s);
    test_encode_msg_i16s(&frame_i16s);
    test_encode_msg_i32s(&frame_i32s);
    test_encode_msg_i64s(&frame_i64s);
    test_encode_msg_f32s(&frame_f32s);
    test_encode_msg_f64s(&frame_f64s);

    printf("\033[34m\nRunning Encoding Tests on Big Endian...\033[0m\n\n");

    test_encode_msg_u8b(&frame_u8b);
    test_encode_msg_u16b(&frame_u16b);
    test_encode_msg_u32b(&frame_u32b);
    test_encode_msg_u64b(&frame_u64b);
    test_encode_msg_i8b(&frame_i8b);
    test_encode_msg_i16b(&frame_i16b);
    test_encode_msg_i32b(&frame_i32b);
    test_encode_msg_i64b(&frame_i64b);
    test_encode_msg_f32b(&frame_f32b);
    test_encode_msg_f64b(&frame_f64b);

    printf("\033[34m\nRunning Decoding Tests on Little Endian...\033[0m\n\n");

    test_decode_msg_u8s(&msg_u8s, &frame_u8s);
    test_decode_msg_u16s(&msg_u16s, &frame_u16s);
    test_decode_msg_u32s(&msg_u32s, &frame_u32s);
    test_decode_msg_u64s(&msg_u64s, &frame_u64s);
    test_decode_msg_i8s(&msg_i8s, &frame_i8s);
    test_decode_msg_i16s(&msg_i16s, &frame_i16s);
    test_decode_msg_i32s(&msg_i32s, &frame_i32s);
    test_decode_msg_i64s(&msg_i64s, &frame_i64s);
    test_decode_msg_f32s(&msg_f32s, &frame_f32s);
    test_decode_msg_f64s(&msg_f64s, &frame_f64s);

    printf("\033[34m\nRunning Decoding Tests on Big Endian...\033[0m\n\n");

    test_decode_msg_u8b(&msg_u8b, &frame_u8b);
    test_decode_msg_u16b(&msg_u16b, &frame_u16b);
    test_decode_msg_u32b(&msg_u32b, &frame_u32b);
    test_decode_msg_u64b(&msg_u64b, &frame_u64b);
    test_decode_msg_i8b(&msg_i8b, &frame_i8b);
    test_decode_msg_i16b(&msg_i16b, &frame_i16b);
    test_decode_msg_i32b(&msg_i32b, &frame_i32b);
    test_decode_msg_i64b(&msg_i64b, &frame_i64b);
    test_decode_msg_f32b(&msg_f32b, &frame_f32b);
    test_decode_msg_f64b(&msg_f64b, &frame_f64b);

    ASSERT_TESTS();

    return 0;
}
