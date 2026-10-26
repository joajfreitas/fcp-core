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

void test_encode_msg() {
    CANMsgFoo msg = {
        .s1 = 123,
        .s2 = 0xAB12,
    };

    CANFrame expected_frame = {
        .ide = 0,
        .sid = 10,
        .dlc = 2,
        .data = {123, 0x12, 0xAB},
    };

    CANFrame frame = can_encode_msg_foo(&msg);
    VERIFY_TEST(frame.sid == expected_frame.sid);
}

void test_is_dev_msg() {
    CANFrame test_frame = {
        .ide = 0,
        .sid = 10,
        .dlc = 2,
        .data = {123, 0x12, 0xAB},
    };

    VERIFY_TEST(can_is_ecu_msg(&test_frame));
}

void test_dlc() {
    CANFrame frame = {
        .ide = 0,
        .sid = 10,
        .dlc = 3,
        .data = {123, 0x12, 0xAB},
    };

    VERIFY_TEST(frame.dlc == 3);
}

void test_decode_msg() {
    CANFrame test_frame = {
        .ide = 0,
        .sid = 10,
        .dlc = 2,
        .data = {123, 0x12, 0xAB},
    };

    CANMsgFoo expected_msg = {
        .s1 = 123,
        .s2 = 0xAB12,
    };

    CANMsgFoo msg = can_decode_msg_foo(&test_frame);

    bool signals_match = msg.s1 == expected_msg.s1 && msg.s2 == expected_msg.s2;
    VERIFY_TEST(signals_match);
}

void test_float_value() {
    CANMsgBar msg = {
        .s1 = 3.14,
    };

    CANFrame f = can_encode_msg_bar(&msg);
    CANMsgBar decoded = can_decode_msg_bar(&f);

    VERIFY_TEST(msg.s1 == decoded.s1);
}

void test_double_value() {
    CANMsgBaz msg = {
        .s1 = 3.14159265359,
    };

    CANFrame f = can_encode_msg_baz(&msg);
    CANMsgBaz decoded = can_decode_msg_baz(&f);

    VERIFY_TEST(msg.s1 == decoded.s1);
}

int main() {
    test_encode_msg();
    test_is_dev_msg();
    test_dlc();
    test_decode_msg();

    ASSERT_TESTS();

    return 0;
}
