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
        .e = C,           // InnerEnum (no prefix needed)
        .s = {            // Nested struct
            .s1 = 33,     // InnerStruct s1
            .s2 = 4567,   // InnerStruct s2
        }
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
    
    VERIFY_TEST(decoded.e == msg.e);
    VERIFY_TEST(decoded.s.s1 == msg.s.s1);  // Access via nested struct
    VERIFY_TEST(decoded.s.s2 == msg.s.s2);  // Access via nested struct
}

void test_outer_struct() {
    CanMsgOuterStruct msg = {
        .inner = {
            .s1 = 10,
            .s2 = 2000,
        },
        .val = 9999
    };

    // Encode
    CanFrame frame = can_encode_msg_outer_struct(&msg);
    VERIFY_TEST(frame.id == CAN_MSG_ID_OUTER_STRUCT);

    // Decode
    CanMsgOuterStruct decoded = can_decode_msg_outer_struct(&frame);
    VERIFY_TEST(decoded.inner.s1 == msg.inner.s1);
    VERIFY_TEST(decoded.inner.s2 == msg.inner.s2);
    VERIFY_TEST(decoded.val == msg.val);
}

void test_multi_level_struct() {
    CanMsgMultiLevelStruct msg = {
        .x = {
            .s1 = 5,
            .s2 = 100,
        },
        .y = {
            .inner = {
                .s1 = 20,
                .s2 = 3000,
            },
            .val = 12345
        }
    };

    // Encode
    CanFrame frame = can_encode_msg_multi_level_struct(&msg);
    VERIFY_TEST(frame.id == CAN_MSG_ID_MULTI_LEVEL_STRUCT);

    // Decode
    CanMsgMultiLevelStruct decoded = can_decode_msg_multi_level_struct(&frame);
    VERIFY_TEST(decoded.x.s1 == msg.x.s1);
    VERIFY_TEST(decoded.x.s2 == msg.x.s2);
    VERIFY_TEST(decoded.y.inner.s1 == msg.y.inner.s1);
    VERIFY_TEST(decoded.y.inner.s2 == msg.y.inner.s2);
    VERIFY_TEST(decoded.y.val == msg.y.val);
}

int main() {
    test_encode_decode_msg();
    test_outer_struct();
    test_multi_level_struct();
    
    ASSERT_TESTS();
    return 0;
}