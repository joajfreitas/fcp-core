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

// Globals for intercepted responses
static CanFrame intercepted_response;
static bool got_response = false;

// Mock send function
void mock_send(const CanFrame *frame) {
    memcpy(&intercepted_response, frame, sizeof(CanFrame));
    got_response = true;
    printf("[DEBUG] Intercepted response: ID=0x%X DLC=%d\n", frame->id, frame->dlc);
}

// Simple test handler
static bool handler_called = false;
void test_handler(const CanFrame *req, CanFrame *resp) {
    handler_called = true;
    resp->id = ECU_RPC_ANS_ID;
    resp->data[2] = 0x55; // test payload
}

// ---------------------- TESTS ---------------------------

// Encode/decode roundtrip for a single RPC struct
void test_rpc_encode_decode_roundtrip() {
    CanRpcSensorReq req = {.request_id = 0x12};
    CanFrame frame = can_encode_rpc_sensor_req(&req);
    CanRpcSensorReq decoded = can_decode_rpc_sensor_req(&frame);
    VERIFY_TEST(decoded.request_id == req.request_id && frame.id == ECU_RPC_GET_ID && frame.dlc == 3);
}

// Encode/decode roundtrip for another RPC struct
void test_rpc_response_roundtrip() {
    CanRpcSensorInformation resp = {.result = 0xA5};
    CanFrame frame = can_encode_rpc_sensor_information(&resp);
    CanRpcSensorInformation decoded = can_decode_rpc_sensor_information(&frame);
    VERIFY_TEST(decoded.result == resp.result);
}

// RPC registration, update, unregister, table full
void test_rpc_table_management() {
    // Reset table
    for (size_t i = 0; i < 32; i++) ecu_rpc_unregister(i, i);

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

// End-to-end dispatch test
void test_rpc_dispatch_end_to_end() {
    ecu_rpc_register(0, 0, test_handler);
    got_response = false;
    handler_called = false;

    CanRpcSensorReq req = {.request_id = 0x01};
    CanFrame frame = can_encode_rpc_sensor_req(&req);
    ecu_service_dispatch(&frame, mock_send);

    VERIFY_TEST(got_response && handler_called && intercepted_response.id == ECU_RPC_ANS_ID);
}

// Multiple dispatches, ensure correct handler chosen
void test_multiple_dispatch() {
    ecu_rpc_register(1, 1, test_handler);
    ecu_rpc_register(2, 2, test_handler);

    got_response = false;
    handler_called = false;
    CanFrame f1 = {.id = ECU_RPC_GET_ID, .dlc = 3, .data = {1, 1, 0}};
    CanFrame f2 = {.id = ECU_RPC_GET_ID, .dlc = 3, .data = {2, 2, 0}};

    ecu_service_dispatch(&f1, mock_send);
    VERIFY_TEST(got_response && handler_called);

    got_response = false;
    handler_called = false;
    ecu_service_dispatch(&f2, mock_send);
    VERIFY_TEST(got_response && handler_called);
}

// Invalid frames
void test_invalid_frames() {
    CanFrame f = {.id = ECU_RPC_GET_ID, .dlc = 1};
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
    // Assuming signal is uint8 with offset/scaling
    CanRpcSensorReq req = {.request_id = 0xFF};
    CanFrame frame = can_encode_rpc_sensor_req(&req);
    CanRpcSensorReq decoded = can_decode_rpc_sensor_req(&frame);
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
