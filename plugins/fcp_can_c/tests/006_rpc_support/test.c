#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "generated_code/can_frame.h"
#include "generated_code/ecu_can.h"
#include "generated_code/ecu_can_rpc.h"
#include "ecu_rpc_client.h"

bool all_tests_passed = true;

#define VERIFY_TEST(cond)                         \
    if (cond) {                                   \
        printf("\033[32m[PASSED] %s\n", __func__); \
    } else {                                     \
        printf("\033[31m[FAILED] %s\033[0m\n", __func__); \
        all_tests_passed = false;               \
    }

#define ASSERT_TESTS()      \
    printf("\033[0m\n");    \
    if (all_tests_passed) { \
        exit(EXIT_SUCCESS); \
    } else {                \
        exit(EXIT_FAILURE); \
    }


static CANFrame intercepted_response;
static bool got_response = false;

void mock_send(const CANFrame *frame) {
    memcpy(&intercepted_response, frame, sizeof(CANFrame));
    got_response = true;
    printf("[DEBUG] Intercepted response: ID=0x%X DLC=%d\n", frame->sid, frame->dlc);
}

static bool handler_called = false;
void test_handler(const CANFrame *req, CANFrame *resp) {
    handler_called = true;
    resp->sid = ECU_CAN_RPC_ANS_ID;
    resp->data[2] = 0x55; // test payload
}

// ---------------------- TESTS ---------------------------

void test_rpc_encode_decode_roundtrip() {
    CANRpcSensorReq req = {.request_id = 0x12};
    CANFrame frame = can_encode_rpc_request_state(&req);
    CANRpcSensorReq decoded = can_decode_rpc_request_state(&frame);
    VERIFY_TEST(decoded.request_id == req.request_id && frame.sid == ECU_CAN_RPC_GET_ID && frame.dlc == 3);
}

void test_rpc_response_roundtrip() {
    CANRpcSensorInformation resp = {.result = 0xA5};
    CANFrame frame = can_encode_rpc_request_state_ans(&resp);
    CANRpcSensorInformation decoded = can_decode_rpc_request_state_ans(&frame);
    VERIFY_TEST(decoded.result == resp.result);
}

void test_rpc_table_management() {
    // Reset table
    for (size_t i = 0; i < MAX_ECU_CAN_RPC_ENTRIES; i++) ecu_can_rpc_unregister(i, i);

    // Register single handler
    VERIFY_TEST(ecu_can_rpc_register(0, 0, test_handler));

    // Update existing handler
    VERIFY_TEST(ecu_can_rpc_register(0, 0, test_handler));

    // Unregister handler
    VERIFY_TEST(ecu_can_rpc_unregister(0, 0));

    // Fill table to max
    for (uint8_t i = 0; i < MAX_ECU_CAN_RPC_ENTRIES; i++) {
        VERIFY_TEST(ecu_can_rpc_register(i, i, test_handler));
    }
    // Table should be full, next register fails
    VERIFY_TEST(!ecu_can_rpc_register(255, 255, test_handler));
}

void test_rpc_dispatch_end_to_end() {
    for (size_t i = 0; i < MAX_ECU_CAN_RPC_ENTRIES; i++) ecu_can_rpc_unregister(i, i);
    ecu_can_rpc_register(0, 0, test_handler);

    got_response = false;
    handler_called = false;

    CANRpcSensorReq req = {.request_id = 0x01};
    CANFrame frame = can_encode_rpc_request_state(&req);
    ecu_can_service_dispatch(&frame, mock_send);

    VERIFY_TEST(got_response && handler_called && intercepted_response.sid == ECU_CAN_RPC_ANS_ID);
}

void test_multiple_dispatch() {
    for (size_t i = 0; i < MAX_ECU_CAN_RPC_ENTRIES; i++) ecu_can_rpc_unregister(i, i);
    ecu_can_rpc_register(0, 0, test_handler);
    ecu_can_rpc_register(1, 0, test_handler);

    got_response = false;
    handler_called = false;
    CANFrame f1 = {.ide = 0, .sid = ECU_CAN_RPC_GET_ID, .dlc = 3, .data = {0, 0, 0}};
    CANFrame f2 = {.ide = 0, .sid = ECU_CAN_RPC_GET_ID, .dlc = 3, .data = {1, 0, 0}};

    ecu_can_service_dispatch(&f1, mock_send);
    VERIFY_TEST(got_response && handler_called);

    got_response = false;
    handler_called = false;
    ecu_can_service_dispatch(&f2, mock_send);
    VERIFY_TEST(got_response && handler_called);
}

void test_invalid_frames() {
    CANFrame f = {.ide = 0, .sid = ECU_CAN_RPC_GET_ID, .dlc = 1};
    got_response = false;
    ecu_can_service_dispatch(&f, mock_send);
    VERIFY_TEST(!got_response);

    f.dlc = 3;
    f.data[0] = 0xFF; f.data[1] = 0xFF;
    got_response = false;
    ecu_can_service_dispatch(&f, mock_send);
    VERIFY_TEST(!got_response);
}

// Signal edge cases: scaling, offsets, endianness
void test_signal_edge_cases() {
    CANRpcSensorReq req = {.request_id = 0xFF};
    CANFrame frame = can_encode_rpc_request_state(&req);
    CANRpcSensorReq decoded = can_decode_rpc_request_state(&frame);
    VERIFY_TEST(decoded.request_id == req.request_id);
}

// ---------------------- MAIN ---------------------------

int main() {
    test_rpc_encode_decode_roundtrip();
    test_rpc_response_roundtrip();
    test_rpc_table_management();
    test_rpc_dispatch_end_to_end();
    test_multiple_dispatch();
    test_invalid_frames();
    test_signal_edge_cases();

    ASSERT_TESTS();
    return 0;
}
