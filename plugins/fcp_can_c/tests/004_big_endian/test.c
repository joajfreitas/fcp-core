#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#include "generated_code/can_frame.h"
#include "generated_code/ecu_can.h"

bool all_tests_passed = true;

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

void test_encode_msg_u16(CanFrame *f) {
    CanFrame expected = {
        .id = CAN_MSG_ID_U16,
        .data = {0x34, 0x12, 0, 0, 0, 0, 0, 0},
        .dlc = 2,
    };

    VERIFY_TEST(compare_frames(f, &expected));
}

void test_encode_msg_u32(CanFrame *f) {
    CanFrame expected = {
        .id = CAN_MSG_ID_U32,
        .data = {0x78, 0x56, 0x34, 0x12, 0, 0, 0, 0},
        .dlc = 4,
    };

    VERIFY_TEST(compare_frames(f, &expected));
}

void test_encode_msg_u64(CanFrame *f) {
    CanFrame expected = {
        .id = CAN_MSG_ID_U64,
        .data = {0xf0, 0xde, 0xbc, 0x9a, 0x78, 0x56, 0x34, 0x12},
        .dlc = 8,
    };

    VERIFY_TEST(compare_frames(f, &expected));
}

void test_encode_msg_f32(CanFrame *f) {
    CanFrame expected = {
        .id = CAN_MSG_ID_F32,
        .data = {0xdb, 0x0f, 0x49, 0x40, 0, 0, 0, 0},
        .dlc = 4,
    };

    VERIFY_TEST(compare_frames(f, &expected));
}

void test_encode_msg_f64(CanFrame *f) {
    CanFrame expected = {
        .id = CAN_MSG_ID_F64,
        .data = {0x18, 0x2d, 0x44, 0x54, 0xfb, 0x21, 0x09, 0x40},
        .dlc = 8,
    };

    VERIFY_TEST(compare_frames(f, &expected));
}

void test_decode_msg_u16(CanMsgU16 *original, CanFrame *f) {
    CanMsgU16 decoded = can_decode_msg_u16(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_decode_msg_u32(CanMsgU32 *original, CanFrame *f) {
    CanMsgU32 decoded = can_decode_msg_u32(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_decode_msg_u64(CanMsgU64 *original, CanFrame *f) {
    CanMsgU64 decoded = can_decode_msg_u64(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_decode_msg_f32(CanMsgF32 *original, CanFrame *f) {
    CanMsgF32 decoded = can_decode_msg_f32(f);

    VERIFY_TEST(original->val == decoded.val);
}

void test_decode_msg_f64(CanMsgF64 *original, CanFrame *f) {
    CanMsgF64 decoded = can_decode_msg_f64(f);

    VERIFY_TEST(original->val == decoded.val);
}

int main() {
    CanMsgU16 msg_u16 = {.val = 0x1234};
    CanMsgU32 msg_u32 = {.val = 0x12345678};
    CanMsgU64 msg_u64 = {.val = 0x123456789abcdef0};
    CanMsgF32 msg_f32 = {.val = 3.14};
    CanMsgF64 msg_f64 = {.val = 3.14159265359};

    CanFrame frame_u16 = can_encode_msg_u16(&msg_u16);
    CanFrame frame_u32 = can_encode_msg_u32(&msg_u32);
    CanFrame frame_u64 = can_encode_msg_u64(&msg_u64);
    CanFrame frame_f32 = can_encode_msg_f32(&msg_f32);
    CanFrame frame_f64 = can_encode_msg_f64(&msg_f64);

    test_encode_msg_u16(&frame_u16);
    test_encode_msg_u32(&frame_u32);
    test_encode_msg_u64(&frame_u64);
    test_encode_msg_f32(&frame_f32);
    test_encode_msg_f64(&frame_f64);

    test_decode_msg_u16(&msg_u16, &frame_u16);
    test_decode_msg_u32(&msg_u32, &frame_u32);
    test_decode_msg_u64(&msg_u64, &frame_u64);
    test_decode_msg_f32(&msg_f32, &frame_f32);
    test_decode_msg_f64(&msg_f64, &frame_f64);

    ASSERT_TESTS();

    return 0;
}
