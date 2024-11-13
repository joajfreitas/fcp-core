#include "generated_code/can_frame.h"
#include "generated_code/ecu_can.h"
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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

int timer = 0;
int call_count = 0;
int sent_ids[10] = {-1, -1, -1, -1, -1, -1, -1, -1, -1, -1};

void reset_fake_can_sender() {
    for (int i = 0; i < 10; i++) {
        sent_ids[i] = -1;
    }
    call_count = 0;
}

void fake_can_sender(const CanFrame *f) { sent_ids[call_count++] = f->id; }

// Time is 0, no messages should be sent
void test_0(CanDeviceEcu *ecu_can) {
    timer = 0;
    call_count = 0;

    can_send_ecu_msgs_scheduled(ecu_can, timer, fake_can_sender);

    VERIFY_TEST(call_count == 0);
}

// Time to send pedals message
void test_1(CanDeviceEcu *ecu_can) {
    timer = 15;
    reset_fake_can_sender();
    can_send_ecu_msgs_scheduled(ecu_can, timer, fake_can_sender);

    VERIFY_TEST(call_count == 1 && sent_ids[0] == CAN_MSG_ID_PEDALS);
}

// Same time as test_1 but message was already sent
void test_2(CanDeviceEcu *ecu_can) {
    timer = 15;
    reset_fake_can_sender();
    can_send_ecu_msgs_scheduled(ecu_can, timer, fake_can_sender);

    VERIFY_TEST(call_count == 0);
}

// Time to send button message
void test_3(CanDeviceEcu *ecu_can) {
    timer = 20;
    reset_fake_can_sender();
    can_send_ecu_msgs_scheduled(ecu_can, timer, fake_can_sender);

    VERIFY_TEST(call_count == 1 && sent_ids[0] == CAN_MSG_ID_SHUTDOWN);
}

// Time send no messages
void test_4(CanDeviceEcu *ecu_can) {
    timer = 25;
    reset_fake_can_sender();
    can_send_ecu_msgs_scheduled(ecu_can, timer, fake_can_sender);

    VERIFY_TEST(call_count == 0);
}

// Send pedals and button messages
void test_5(CanDeviceEcu *ecu_can) {
    timer = 30;
    reset_fake_can_sender();
    can_send_ecu_msgs_scheduled(ecu_can, timer, fake_can_sender);

    VERIFY_TEST(call_count == 2 && sent_ids[0] == CAN_MSG_ID_PEDALS &&
                sent_ids[1] == CAN_MSG_ID_BUTTON);
}

int main() {

    CanDeviceEcu ecu_can = {.pedals.acc_pos = 30,
                            .pedals.brake_pos = 0,
                            .shutdown.error = 212,
                            .button.press = 1};

    CanFrame expected_pedals_frame = can_encode_msg_pedals(&ecu_can.pedals);
    CanFrame expected_shutdown_frame =
        can_encode_msg_shutdown(&ecu_can.shutdown);

    test_0(&ecu_can);
    test_1(&ecu_can);
    test_2(&ecu_can);
    test_3(&ecu_can);
    test_4(&ecu_can);

    ASSERT_TESTS();

    return 0;
}
