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
    if (a->ide != b->ide) {
        return false;
    }
    
    if ((a->sid | (a->eid << 11)) != (b->sid | (b->eid << 11)) && (a->ide == 1 && b->ide == 1)) {
        return false;
    }

    if ((a->sid != b->sid ) && (a->ide == 0 && b->ide == 0)) {
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

void test_encode_msg_u8l(CanFrame *f, CanFrame *f2) {
    CanFrame expected = {
        .ide = 0,
        .sid = CAN_MSG_ID_U8_L,
        .data = {0x12, 0, 0, 0, 0, 0, 0, 0},
        .dlc = 1,
    };
    VERIFY_TEST(compare_frames(f, &expected));

    CanFrame expected2 = {
        .ide = 1,
        .sid = CAN2B_MSG_ID_U8_L & 0x07FF,
        .eid = (CAN2B_MSG_ID_U8_L >> 11) & 0x03FFFF,
        .data = {0x12, 0, 0, 0, 0, 0, 0, 0},
        .dlc = 1,
    };
    VERIFY_TEST(compare_frames(f2, &expected2));
}

void test_decode_msg_u8l(CanMsgU8L *original, CanFrame *f, CanFrame *f2) {
    CanMsgU8L decoded = can_decode_msg_u8_l(f);

    VERIFY_TEST(original->val == decoded.val);

    decoded = can2b_decode_msg_u8_l(f2);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_u16l(CanFrame *f, CanFrame *f2) {
    CanFrame expected = {
        .ide = 0,
        .sid = CAN_MSG_ID_U16_L,
        .data = {0x34, 0x12, 0, 0, 0, 0, 0, 0},
        .dlc = 2,
    };
    VERIFY_TEST(compare_frames(f, &expected));

    CanFrame expected2 = {
        .ide = 1,
        .sid = CAN2B_MSG_ID_U16_L & 0x07FF,
        .eid = (CAN2B_MSG_ID_U16_L >> 11) & 0x03FFFF,
        .data = {0x34, 0x12, 0, 0, 0, 0, 0, 0},
        .dlc = 2,
    };
    VERIFY_TEST(compare_frames(f2, &expected2));
}

void test_decode_msg_u16l(CanMsgU16L *original, CanFrame *f, CanFrame *f2) {
    CanMsgU16L decoded = can_decode_msg_u16_l(f);

    VERIFY_TEST(original->val == decoded.val);

    decoded = can2b_decode_msg_u16_l(f2);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_u32l(CanFrame *f, CanFrame *f2) {
    CanFrame expected = {
        .ide = 0,
        .sid = CAN_MSG_ID_U32_L,
        .data = {0x78, 0x56, 0x34, 0x12, 0, 0, 0, 0},
        .dlc = 4,
    };
    VERIFY_TEST(compare_frames(f, &expected));

    CanFrame expected2 = {
        .ide = 1,
        .sid = CAN2B_MSG_ID_U32_L & 0x07FF,
        .eid = (CAN2B_MSG_ID_U32_L >> 11) & 0x03FFFF,
        .data = {0x78, 0x56, 0x34, 0x12, 0, 0, 0, 0},
        .dlc = 4,
    };
    VERIFY_TEST(compare_frames(f2, &expected2));
}

void test_decode_msg_u32l(CanMsgU32L *original, CanFrame *f, CanFrame *f2) {
    CanMsgU32L decoded = can_decode_msg_u32_l(f);

    VERIFY_TEST(original->val == decoded.val);

    decoded = can2b_decode_msg_u32_l(f2);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_u64l(CanFrame *f, CanFrame *f2) {
    CanFrame expected = {
        .ide = 0,
        .sid = CAN_MSG_ID_U64_L,
        .data = {0xF0, 0xDE, 0xBC, 0x9A, 0x78, 0x56, 0x34, 0x12},
        .dlc = 8,
    };
    VERIFY_TEST(compare_frames(f, &expected));

    CanFrame expected2 = {
        .ide = 1,
        .sid = CAN2B_MSG_ID_U64_L & 0x07FF,
        .eid = (CAN2B_MSG_ID_U64_L >> 11) & 0x03FFFF,
        .data = {0xF0, 0xDE, 0xBC, 0x9A, 0x78, 0x56, 0x34, 0x12},
        .dlc = 8,
    };
    VERIFY_TEST(compare_frames(f2, &expected2));
}

void test_decode_msg_u64l(CanMsgU64L *original, CanFrame *f, CanFrame *f2) {
    CanMsgU64L decoded = can_decode_msg_u64_l(f);

    VERIFY_TEST(original->val == decoded.val);

    decoded = can2b_decode_msg_u64_l(f2);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_i8l(CanFrame *f, CanFrame *f2) {
    CanFrame expected = {
        .ide = 0,
        .sid = CAN_MSG_ID_I8_L,
        .data = {0x12, 0, 0, 0, 0, 0, 0, 0},
        .dlc = 1,
    };
    VERIFY_TEST(compare_frames(f, &expected));

    CanFrame expected2 = {
        .ide = 1,
        .sid = CAN2B_MSG_ID_I8_L & 0x07FF,
        .eid = (CAN2B_MSG_ID_I8_L >> 11) & 0x03FFFF,
        .data = {0x12, 0, 0, 0, 0, 0, 0, 0},
        .dlc = 1,
    };
    VERIFY_TEST(compare_frames(f2, &expected2));
}

void test_decode_msg_i8l(CanMsgI8L *original, CanFrame *f, CanFrame *f2) {
    CanMsgI8L decoded = can_decode_msg_i8_l(f);

    VERIFY_TEST(original->val == decoded.val);

    decoded = can2b_decode_msg_i8_l(f2);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_i16l(CanFrame *f, CanFrame *f2) {
    CanFrame expected = {
        .ide = 0,
        .sid = CAN_MSG_ID_I16_L,
        .data = {0x34, 0x12, 0, 0, 0, 0, 0, 0},
        .dlc = 2,
    };
    VERIFY_TEST(compare_frames(f, &expected));

    CanFrame expected2 = {
        .ide = 1,
        .sid = CAN2B_MSG_ID_I16_L & 0x07FF,
        .eid = (CAN2B_MSG_ID_I16_L >> 11) & 0x03FFFF,
        .data = {0x34, 0x12, 0, 0, 0, 0, 0, 0},
        .dlc = 2,
    };
    VERIFY_TEST(compare_frames(f2, &expected2));
}

void test_decode_msg_i16l(CanMsgI16L *original, CanFrame *f, CanFrame *f2) {
    CanMsgI16L decoded = can_decode_msg_i16_l(f);

    VERIFY_TEST(original->val == decoded.val);

    decoded = can2b_decode_msg_i16_l(f2);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_i32l(CanFrame *f, CanFrame *f2) {
    CanFrame expected = {
        .ide = 0,
        .sid = CAN_MSG_ID_I32_L,
        .data = {0x78, 0x56, 0x34, 0x12, 0, 0, 0, 0},
        .dlc = 4,
    };
    VERIFY_TEST(compare_frames(f, &expected));

    CanFrame expected2 = {
        .ide = 1,
        .sid = CAN2B_MSG_ID_I32_L & 0x07FF,
        .eid = (CAN2B_MSG_ID_I32_L >> 11) & 0x03FFFF,
        .data = {0x78, 0x56, 0x34, 0x12, 0, 0, 0, 0},
        .dlc = 4,
    };
    VERIFY_TEST(compare_frames(f2, &expected2));
}

void test_decode_msg_i32l(CanMsgI32L *original, CanFrame *f, CanFrame *f2) {
    CanMsgI32L decoded = can_decode_msg_i32_l(f);

    VERIFY_TEST(original->val == decoded.val);

    decoded = can2b_decode_msg_i32_l(f2);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_i64l(CanFrame *f, CanFrame *f2) {
    CanFrame expected = {
        .ide = 0,
        .sid = CAN_MSG_ID_I64_L,
        .data = {0xF0, 0xDE, 0xBC, 0x9A, 0x78, 0x56, 0x34, 0x12},
        .dlc = 8,
    };
    VERIFY_TEST(compare_frames(f, &expected));

    CanFrame expected2 = {
        .ide = 1,
        .sid = CAN2B_MSG_ID_I64_L & 0x07FF,
        .eid = (CAN2B_MSG_ID_I64_L >> 11) & 0x03FFFF,
        .data = {0xF0, 0xDE, 0xBC, 0x9A, 0x78, 0x56, 0x34, 0x12},
        .dlc = 8,
    };
    VERIFY_TEST(compare_frames(f2, &expected2));
}

void test_decode_msg_i64l(CanMsgI64L *original, CanFrame *f, CanFrame *f2) {
    CanMsgI64L decoded = can_decode_msg_i64_l(f);

    VERIFY_TEST(original->val == decoded.val);

    decoded = can2b_decode_msg_i64_l(f2);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_f32l(CanFrame *f, CanFrame *f2) {
    F32 v = {.f = 5.843f};

    CanFrame expected = {
        .ide = 0,
        .sid = CAN_MSG_ID_F32_L,
        .data = {v.i, v.i >> 8, v.i >> 16, v.i >> 24, 0, 0, 0, 0},
        .dlc = 4,
    };
    VERIFY_TEST(compare_frames(f, &expected));

    CanFrame expected2 = {
        .ide = 1,
        .sid = CAN2B_MSG_ID_F32_L & 0x07FF,
        .eid = (CAN2B_MSG_ID_F32_L >> 11) & 0x03FFFF,
        .data = {v.i, v.i >> 8, v.i >> 16, v.i >> 24, 0, 0, 0, 0},
        .dlc = 4,
    };
    VERIFY_TEST(compare_frames(f2, &expected2));
}

void test_decode_msg_f32l(CanMsgF32L *original, CanFrame *f, CanFrame *f2) {
    CanMsgF32L decoded = can_decode_msg_f32_l(f);

    VERIFY_TEST(original->val == decoded.val);

    decoded = can2b_decode_msg_f32_l(f2);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_f64l(CanFrame *f, CanFrame *f2) {
    F64 v = {.d = 5.84367431557};

    CanFrame expected = {
        .ide = 0,
        .sid = CAN_MSG_ID_F64_L,
        .data = {v.i, v.i >> 8, v.i >> 16, v.i >> 24, v.i >> 32, v.i >> 40, v.i >> 48, v.i >> 56},
        .dlc = 8,
    };
    VERIFY_TEST(compare_frames(f, &expected));

    CanFrame expected2 = {
        .ide = 1,
        .sid = CAN2B_MSG_ID_F64_L & 0x07FF,
        .eid = (CAN2B_MSG_ID_F64_L >> 11) & 0x03FFFF,
        .data = {v.i, v.i >> 8, v.i >> 16, v.i >> 24, v.i >> 32, v.i >> 40, v.i >> 48, v.i >> 56},
        .dlc = 8,
    };
    VERIFY_TEST(compare_frames(f2, &expected2));
}

void test_decode_msg_f64l(CanMsgF64L *original, CanFrame *f, CanFrame *f2) {
    CanMsgF64L decoded = can_decode_msg_f64_l(f);

    VERIFY_TEST(original->val == decoded.val);

    decoded = can2b_decode_msg_f64_l(f2);

    VERIFY_TEST(original->val == decoded.val);
}


int main() {
    printf("Running Tests...\n\n");

    CanMsgU8L msg_u8l = {.val = 0x12};
    CanMsgU16L msg_u16l = {.val = 0x1234};
    CanMsgU32L msg_u32l = {.val = 0x12345678};
    CanMsgU64L msg_u64l = {.val = 0x123456789abcdef0};
    CanMsgI8L msg_i8l = {.val = 0x12};
    CanMsgI16L msg_i16l = {.val = 0x1234};
    CanMsgI32L msg_i32l = {.val = 0x12345678};
    CanMsgI64L msg_i64l = {.val = 0x123456789abcdef0};
    CanMsgF32L msg_f32l = {.val = 5.843};
    CanMsgF64L msg_f64l = {.val = 5.84367431557};

    CanFrame frame_u8l = can_encode_msg_u8_l(&msg_u8l);
    CanFrame frame_u16l = can_encode_msg_u16_l(&msg_u16l);
    CanFrame frame_u32l = can_encode_msg_u32_l(&msg_u32l);
    CanFrame frame_u64l = can_encode_msg_u64_l(&msg_u64l);
    CanFrame frame_i8l = can_encode_msg_i8_l(&msg_i8l);
    CanFrame frame_i16l = can_encode_msg_i16_l(&msg_i16l);
    CanFrame frame_i32l = can_encode_msg_i32_l(&msg_i32l);
    CanFrame frame_i64l = can_encode_msg_i64_l(&msg_i64l);
    CanFrame frame_f32l = can_encode_msg_f32_l(&msg_f32l);
    CanFrame frame_f64l = can_encode_msg_f64_l(&msg_f64l);

    CanFrame frame_u8l_2 = can2b_encode_msg_u8_l(&msg_u8l);
    CanFrame frame_u16l_2 = can2b_encode_msg_u16_l(&msg_u16l);
    CanFrame frame_u32l_2 = can2b_encode_msg_u32_l(&msg_u32l);
    CanFrame frame_u64l_2 = can2b_encode_msg_u64_l(&msg_u64l);
    CanFrame frame_i8l_2 = can2b_encode_msg_i8_l(&msg_i8l);
    CanFrame frame_i16l_2 = can2b_encode_msg_i16_l(&msg_i16l);
    CanFrame frame_i32l_2 = can2b_encode_msg_i32_l(&msg_i32l);
    CanFrame frame_i64l_2 = can2b_encode_msg_i64_l(&msg_i64l);
    CanFrame frame_f32l_2 = can2b_encode_msg_f32_l(&msg_f32l);
    CanFrame frame_f64l_2 = can2b_encode_msg_f64_l(&msg_f64l);

    printf("\033[34m\nRunning Encoding Tests on Little Endian...\033[0m\n\n");

    test_encode_msg_u8l(&frame_u8l, &frame_u8l_2);
    test_encode_msg_u16l(&frame_u16l, &frame_u16l_2);
    test_encode_msg_u32l(&frame_u32l, &frame_u32l_2);
    test_encode_msg_u64l(&frame_u64l, &frame_u64l_2);
    test_encode_msg_i8l(&frame_i8l, &frame_i8l_2);
    test_encode_msg_i16l(&frame_i16l, &frame_i16l_2);
    test_encode_msg_i32l(&frame_i32l, &frame_i32l_2);
    test_encode_msg_i64l(&frame_i64l, &frame_i64l_2);
    test_encode_msg_f32l(&frame_f32l, &frame_f32l_2);
    test_encode_msg_f64l(&frame_f64l, &frame_f64l_2);

    printf("\033[34m\nRunning Decoding Tests on Little Endian...\033[0m\n\n");

    test_decode_msg_u8l(&msg_u8l, &frame_u8l, &frame_u8l_2);
    test_decode_msg_u16l(&msg_u16l, &frame_u16l, &frame_u16l_2);
    test_decode_msg_u32l(&msg_u32l, &frame_u32l, &frame_u32l_2);
    test_decode_msg_u64l(&msg_u64l, &frame_u64l, &frame_u64l_2);
    test_decode_msg_i8l(&msg_i8l, &frame_i8l, &frame_i8l_2);
    test_decode_msg_i16l(&msg_i16l, &frame_i16l, &frame_i16l_2);
    test_decode_msg_i32l(&msg_i32l, &frame_i32l, &frame_i32l_2);
    test_decode_msg_i64l(&msg_i64l, &frame_i64l, &frame_i64l_2);
    test_decode_msg_f32l(&msg_f32l, &frame_f32l, &frame_f32l_2);
    test_decode_msg_f64l(&msg_f64l, &frame_f64l, &frame_f64l_2);

    ASSERT_TESTS();

    return 0;
}
