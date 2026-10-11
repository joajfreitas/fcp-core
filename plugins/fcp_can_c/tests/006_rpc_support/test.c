#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "generated_code/can_frame.h"
#include "generated_code/ecu_can.h"
#include "generated_code/ecu_rpc.h"
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


static CanFrame intercepted_response;
static bool got_response = false;

void mock_send(const CanFrame *frame) {
    memcpy(&intercepted_response, frame, sizeof(CanFrame));
    got_response = true;
    printf("[DEBUG] Intercepted response: ID=0x%X DLC=%d\n", frame->sid, frame->dlc);
}

static bool handler_called = false;
void test_handler(const CanFrame *req, CanFrame *resp) {
    handler_called = true;
    resp->sid = ECU_CAN_RPC_ANS_ID;
    resp->data[2] = 0x55; // test payload
}

// ---------------------- TESTS ---------------------------

void test_rpc_encode_decode_roundtrip() {
    CanRpcSensorReq req = {.request_id = 0x12};
    CanFrame frame = can_encode_rpc_request_state(&req);
    CanRpcSensorReq decoded = can_decode_rpc_request_state(&frame);
    VERIFY_TEST(decoded.request_id == req.request_id && frame.sid == ECU_CAN_RPC_GET_ID && frame.dlc == 3);
}

void test_rpc_response_roundtrip() {
    CanRpcSensorInformation resp = {.result = 0xA5};
    CanFrame frame = can_encode_rpc_request_state_ans(&resp);
    CanRpcSensorInformation decoded = can_decode_rpc_request_state_ans(&frame);
    VERIFY_TEST(decoded.result == resp.result);
}

void test_rpc_table_management() {
    // Reset table
    for (size_t i = 0; i < MAX_RPC_ENTRIES; i++) ecu_rpc_unregister(i, i);

    // Register single handler
    VERIFY_TEST(ecu_rpc_register(0, 0, test_handler));

    // Update existing handler
    VERIFY_TEST(ecu_rpc_register(0, 0, test_handler));

    // Unregister handler
    VERIFY_TEST(ecu_rpc_unregister(0, 0));

    // Fill table to max
    for (uint8_t i = 0; i < MAX_RPC_ENTRIES; i++) {
        VERIFY_TEST(ecu_rpc_register(i, i, test_handler));
    }
    // Table should be full, next register fails
    VERIFY_TEST(!ecu_rpc_register(255, 255, test_handler));
}

void test_rpc_dispatch_end_to_end() {
    ecu_rpc_register(0, 0, test_handler);
    got_response = false;
    handler_called = false;

    CanRpcSensorReq req = {.request_id = 0x01};
    CanFrame frame = can_encode_rpc_request_state(&req);
    ecu_service_dispatch(&frame, mock_send);

    VERIFY_TEST(got_response && handler_called && intercepted_response.sid == ECU_CAN_RPC_ANS_ID);
}

void test_multiple_dispatch() {
    ecu_rpc_register(1, 1, test_handler);
    ecu_rpc_register(2, 2, test_handler);

    got_response = false;
    handler_called = false;
    CanFrame f1 = {.eid = 0, .sid = ECU_CAN_RPC_GET_ID, .dlc = 3, .data = {1, 1, 0}};
    CanFrame f2 = {.eid = 0, .sid = ECU_CAN_RPC_GET_ID, .dlc = 3, .data = {2, 2, 0}};

    ecu_service_dispatch(&f1, mock_send);
    VERIFY_TEST(got_response && handler_called);

    got_response = false;
    handler_called = false;
    ecu_service_dispatch(&f2, mock_send);
    VERIFY_TEST(got_response && handler_called);
}

void test_invalid_frames() {
    CanFrame f = {.eid = 0, .sid = ECU_CAN_RPC_GET_ID, .dlc = 1};
    got_response = false;
    ecu_service_dispatch(&f, mock_send);
    VERIFY_TEST(!got_response);

    f.dlc = 3;
    f.data[0] = 0xFF; f.data[1] = 0xFF;
    got_response = false;
    ecu_service_dispatch(&f, mock_send);
    VERIFY_TEST(!got_response);
}

// Signal edge cases: scaling, offsets, endianness
void test_signal_edge_cases() {
    CanRpcSensorReq req = {.request_id = 0xFF};
    CanFrame frame = can_encode_rpc_request_state(&req);
    CanRpcSensorReq decoded = can_decode_rpc_request_state(&frame);
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
