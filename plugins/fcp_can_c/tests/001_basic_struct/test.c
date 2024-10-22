#include "generated_code/can_frame.h"
#include "generated_code/ecu_can.h"
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

bool all_tests_passed = true;

#define VERIFY_TEST(condition)                                                 \
    if (condition) {                                                           \
        printf("\033[32m [PASSED] %s\n", __func__);                            \
    } else {                                                                   \
        printf("\033[31m [FAILED] %s\033[0m\n", __func__);                     \
        all_tests_passed = false;                                              \
    }

#define ASSERT_TESTS()                                                         \
    printf("\033[0m");                                                         \
    if (all_tests_passed) {                                                    \
        exit(EXIT_SUCCESS);                                                    \
    } else {                                                                   \
        exit(EXIT_FAILURE);                                                    \
    }

CanFrame expected_frame = {
    .id = 10,
    .dlc = 2,
    .data = {123, 234},
};

void test_encode_msg() {
    CanMsgFoo msg = {
        .s1 = 123,
        .s2 = 234,
    };

    CanFrame frame = can_encode_msg_foo(&msg);
    VERIFY_TEST(frame.id == expected_frame.id);
}

void test_is_dev_msg() { VERIFY_TEST(can_is_ecu_msg(&expected_frame)); }

void test_dlc() { VERIFY_TEST(expected_frame.dlc == 2); }

void test_decode_msg() {
    CanMsgFoo expected_msg = {
        .s1 = 123,
        .s2 = 234,
    };

    CanMsgFoo msg = can_decode_msg_foo(&expected_frame);

    bool signals_match = msg.s1 == expected_msg.s1 && msg.s2 == expected_msg.s2;
    VERIFY_TEST(signals_match);
}

int main() {
    CanMsgFoo msg = {
        .s1 = 123,
        .s2 = 234,
    };

    CanFrame frame = can_encode_msg_foo(&msg);

    test_encode_msg();
    test_is_dev_msg();
    test_dlc();
    test_decode_msg();

    ASSERT_TESTS();

    return 0;
}
