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

bool compare_frames(CANFrame *a, CANFrame *b) {
    if (a->ide != b->ide) {
        return false;
    }

    if (a->sid != b->sid) {
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

void test_encode_msg_u8l(CANFrame *f) {
    CANFrame expected = {
        .ide = 0,
        .sid = CAN_MSG_ID_U8_L,
        .data = {0x12, 0, 0, 0, 0, 0, 0, 0},
        .dlc = 1,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_u8l(CANMsgU8L *original, CANFrame *f) {
    CANMsgU8L decoded = can_decode_msg_u8_l(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_u16l(CANFrame *f) {
    CANFrame expected = {
        .ide = 0,
        .sid = CAN_MSG_ID_U16_L,
        .data = {0x34, 0x12, 0, 0, 0, 0, 0, 0},
        .dlc = 2,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_u16l(CANMsgU16L *original, CANFrame *f) {
    CANMsgU16L decoded = can_decode_msg_u16_l(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_u32l(CANFrame *f) {
    CANFrame expected = {
        .ide = 0,
        .sid = CAN_MSG_ID_U32_L,
        .data = {0x78, 0x56, 0x34, 0x12, 0, 0, 0, 0},
        .dlc = 4,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_u32l(CANMsgU32L *original, CANFrame *f) {
    CANMsgU32L decoded = can_decode_msg_u32_l(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_u64l(CANFrame *f) {
    CANFrame expected = {
        .ide = 0,
        .sid = CAN_MSG_ID_U64_L,
        .data = {0xF0, 0xDE, 0xBC, 0x9A, 0x78, 0x56, 0x34, 0x12},
        .dlc = 8,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_u64l(CANMsgU64L *original, CANFrame *f) {
    CANMsgU64L decoded = can_decode_msg_u64_l(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_i8l(CANFrame *f) {
    CANFrame expected = {
        .ide = 0,
        .sid = CAN_MSG_ID_I8_L,
        .data = {0x12, 0, 0, 0, 0, 0, 0, 0},
        .dlc = 1,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_i8l(CANMsgI8L *original, CANFrame *f) {
    CANMsgI8L decoded = can_decode_msg_i8_l(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_i16l(CANFrame *f) {
    CANFrame expected = {
        .ide = 0,
        .sid = CAN_MSG_ID_I16_L,
        .data = {0x34, 0x12, 0, 0, 0, 0, 0, 0},
        .dlc = 2,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_i16l(CANMsgI16L *original, CANFrame *f) {
    CANMsgI16L decoded = can_decode_msg_i16_l(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_i32l(CANFrame *f) {
    CANFrame expected = {
        .ide = 0,
        .sid = CAN_MSG_ID_I32_L,
        .data = {0x78, 0x56, 0x34, 0x12, 0, 0, 0, 0},
        .dlc = 4,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_i32l(CANMsgI32L *original, CANFrame *f) {
    CANMsgI32L decoded = can_decode_msg_i32_l(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_i64l(CANFrame *f) {
    CANFrame expected = {
        .ide = 0,
        .sid = CAN_MSG_ID_I64_L,
        .data = {0xF0, 0xDE, 0xBC, 0x9A, 0x78, 0x56, 0x34, 0x12},
        .dlc = 8,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_i64l(CANMsgI64L *original, CANFrame *f) {
    CANMsgI64L decoded = can_decode_msg_i64_l(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_f32l(CANFrame *f) {
    F32 v = {.f = 5.843f};

    CANFrame expected = {
        .ide = 0,
        .sid = CAN_MSG_ID_F32_L,
        .data = {v.i, v.i >> 8, v.i >> 16, v.i >> 24, 0, 0, 0, 0},
        .dlc = 4,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_f32l(CANMsgF32L *original, CANFrame *f) {
    CANMsgF32L decoded = can_decode_msg_f32_l(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_encode_msg_f64l(CANFrame *f) {
    F64 v = {.d = 5.84367431557};

    CANFrame expected = {
        .ide = 0,
        .sid = CAN_MSG_ID_F64_L,
        .data = {v.i, v.i >> 8, v.i >> 16, v.i >> 24, v.i >> 32, v.i >> 40, v.i >> 48, v.i >> 56},
        .dlc = 8,
    };
    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_f64l(CANMsgF64L *original, CANFrame *f) {
    CANMsgF64L decoded = can_decode_msg_f64_l(f);

    VERIFY_TEST(original->val == decoded.val);
}


int main() {
    printf("Running Tests...\n\n");

    CANMsgU8L msg_u8l = {.val = 0x12};
    CANMsgU16L msg_u16l = {.val = 0x1234};
    CANMsgU32L msg_u32l = {.val = 0x12345678};
    CANMsgU64L msg_u64l = {.val = 0x123456789abcdef0};
    CANMsgI8L msg_i8l = {.val = 0x12};
    CANMsgI16L msg_i16l = {.val = 0x1234};
    CANMsgI32L msg_i32l = {.val = 0x12345678};
    CANMsgI64L msg_i64l = {.val = 0x123456789abcdef0};
    CANMsgF32L msg_f32l = {.val = 5.843};
    CANMsgF64L msg_f64l = {.val = 5.84367431557};

    CANFrame frame_u8l = can_encode_msg_u8_l(&msg_u8l);
    CANFrame frame_u16l = can_encode_msg_u16_l(&msg_u16l);
    CANFrame frame_u32l = can_encode_msg_u32_l(&msg_u32l);
    CANFrame frame_u64l = can_encode_msg_u64_l(&msg_u64l);
    CANFrame frame_i8l = can_encode_msg_i8_l(&msg_i8l);
    CANFrame frame_i16l = can_encode_msg_i16_l(&msg_i16l);
    CANFrame frame_i32l = can_encode_msg_i32_l(&msg_i32l);
    CANFrame frame_i64l = can_encode_msg_i64_l(&msg_i64l);
    CANFrame frame_f32l = can_encode_msg_f32_l(&msg_f32l);
    CANFrame frame_f64l = can_encode_msg_f64_l(&msg_f64l);

    printf("\033[34m\nRunning Encoding Tests on Little Endian...\033[0m\n\n");

    test_encode_msg_u8l(&frame_u8l);
    test_encode_msg_u16l(&frame_u16l);
    test_encode_msg_u32l(&frame_u32l);
    test_encode_msg_u64l(&frame_u64l);
    test_encode_msg_i8l(&frame_i8l);
    test_encode_msg_i16l(&frame_i16l);
    test_encode_msg_i32l(&frame_i32l);
    test_encode_msg_i64l(&frame_i64l);
    test_encode_msg_f32l(&frame_f32l);
    test_encode_msg_f64l(&frame_f64l);

    printf("\033[34m\nRunning Decoding Tests on Little Endian...\033[0m\n\n");

    test_decode_msg_u8l(&msg_u8l, &frame_u8l);
    test_decode_msg_u16l(&msg_u16l, &frame_u16l);
    test_decode_msg_u32l(&msg_u32l, &frame_u32l);
    test_decode_msg_u64l(&msg_u64l, &frame_u64l);
    test_decode_msg_i8l(&msg_i8l, &frame_i8l);
    test_decode_msg_i16l(&msg_i16l, &frame_i16l);
    test_decode_msg_i32l(&msg_i32l, &frame_i32l);
    test_decode_msg_i64l(&msg_i64l, &frame_i64l);
    test_decode_msg_f32l(&msg_f32l, &frame_f32l);
    test_decode_msg_f64l(&msg_f64l, &frame_f64l);

    ASSERT_TESTS();

    return 0;
}
