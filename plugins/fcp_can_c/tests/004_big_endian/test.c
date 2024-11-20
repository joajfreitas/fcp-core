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

void test_endianness() {
    CanFrame expected_frame = {
        .id = 10,
        .dlc = 2,
        .data = {0x34, 0x12, 0x56, 0x78},
    };

    CanMsgPedals msg = {
        .acc_pos = 0x1234,
        .brake_pos = 0x5678,
    };

    CanFrame frame = can_encode_msg_pedals(&msg);

    bool equal = true;
    for (int i = 0; i < 4; i++) {
        if (frame.data[i] != expected_frame.data[i]) {
            equal = false;
            break;
        }
    }

    VERIFY_TEST(equal);
}

int main() {
    test_endianness();
    ASSERT_TESTS();

    return 0;
}
