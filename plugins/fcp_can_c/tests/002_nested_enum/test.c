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

void test_encode_decode_sensor_information() {
    CanMsgSensorInformation msg = {
        .e = C,           // InnerEnum
        .l1 = {           // Level1Struct
            .s1 = 7,
            .s2 = 15,
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
    VERIFY_TEST(decoded.l1.s1 == msg.l1.s1);
    VERIFY_TEST(decoded.l1.s2 == msg.l1.s2);
}

void test_level3_struct() {
    CanMsgLevel3Struct msg = {
        .l2 = {                    // Level2Struct
            .l1 = {                // Level1Struct
                .s1 = 10,
                .s2 = 12,
            },
            .val2 = 5,
        },
        .val3 = 9
    };

    // Encode
    CanFrame frame = can_encode_msg_level3_struct(&msg);
    VERIFY_TEST(frame.id == CAN_MSG_ID_LEVEL3_STRUCT);

    // Decode
    CanMsgLevel3Struct decoded = can_decode_msg_level3_struct(&frame);
    VERIFY_TEST(decoded.l2.l1.s1 == msg.l2.l1.s1);
    VERIFY_TEST(decoded.l2.l1.s2 == msg.l2.l1.s2);
    VERIFY_TEST(decoded.l2.val2 == msg.l2.val2);
    VERIFY_TEST(decoded.val3 == msg.val3);
}

void test_level5_struct() {
    CanMsgLevel5Struct msg = {
        .l4 = {                            // Level4Struct
            .l3 = {                        // Level3Struct
                .l2 = {                    // Level2Struct
                    .l1 = {                // Level1Struct
                        .s1 = 5,
                        .s2 = 10,
                    },
                    .val2 = 3,
                },
                .val3 = 12,
            },
            .val4 = 7,
        },
        .e = B,
        .val5 = 15
    };

    // Encode
    CanFrame frame = can_encode_msg_level5_struct(&msg);
    VERIFY_TEST(frame.id == CAN_MSG_ID_LEVEL5_STRUCT);

    // Decode
    CanMsgLevel5Struct decoded = can_decode_msg_level5_struct(&frame);
    VERIFY_TEST(decoded.l4.l3.l2.l1.s1 == msg.l4.l3.l2.l1.s1);
    VERIFY_TEST(decoded.l4.l3.l2.l1.s2 == msg.l4.l3.l2.l1.s2);
    VERIFY_TEST(decoded.l4.l3.l2.val2 == msg.l4.l3.l2.val2);
    VERIFY_TEST(decoded.l4.l3.val3 == msg.l4.l3.val3);
    VERIFY_TEST(decoded.l4.val4 == msg.l4.val4);
    VERIFY_TEST(decoded.e == msg.e);
    VERIFY_TEST(decoded.val5 == msg.val5);
}

int main() {
    printf("=== Running CAN 5-layer nested struct tests ===\n\n");
    
    test_encode_decode_sensor_information();
    test_level3_struct();
    test_level5_struct();
    
    printf("\n=== All tests completed ===\n");
    ASSERT_TESTS();
    return 0;
}