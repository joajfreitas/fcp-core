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

void test_encode_decode_msg() {
    CanMsgSensorInformation msg = {
        .e    = C,      // InnerEnum
        .s_s1 = 33,     // InnerStruct s1
        .s_s2 = 4567,   // InnerStruct s2
    };

    // Encode
    CanFrame frame = can_encode_msg_sensor_information(&msg);

    printf("Encoded frame bytes: ");
    for (int i = 0; i < frame.dlc; i++)
        printf("%d ", frame.data[i]);
    printf("\n");

    VERIFY_TEST(frame.id == CAN_MSG_ID_SENSOR_INFORMATION);

    // Decode
    CanMsgSensorInformation decoded = can_decode_msg_sensor_information(&frame);

    VERIFY_TEST(decoded.e    == msg.e);
    VERIFY_TEST(decoded.s_s1 == msg.s_s1);
    VERIFY_TEST(decoded.s_s2 == msg.s_s2);
}

int main() {
    test_encode_decode_msg();
    ASSERT_TESTS();
    return 0;
}
