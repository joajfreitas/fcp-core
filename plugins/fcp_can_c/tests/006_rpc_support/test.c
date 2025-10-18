#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "generated_code/can_frame.h"
#include "generated_code/ecu_can.h"
#include "generated_code/ecu_rpc.h"
#include "ecu_rpc_client.h"

bool all_tests_passed = true;

#define VERIFY_TEST(condition)                             \
    if (condition) {                                       \
        printf("\033[32m[PASSED] %s\n", __func__);        \
    } else {                                               \
        printf("\033[31m[FAILED] %s\033[0m\n", __func__); \
        all_tests_passed = false;                          \
    }

#define ASSERT_TESTS()      \
    printf("\033[0m\n");    \
    if (all_tests_passed) { \
        exit(EXIT_SUCCESS); \
    } else {                \
        exit(EXIT_FAILURE); \
    }

// Globals for capturing dispatched responses
static CanFrame intercepted_response;
static bool got_response = false;

// Mock send function
void mock_send(const CanFrame *frame) {
    memcpy(&intercepted_response, frame, sizeof(CanFrame));
    got_response = true;
    printf("\033[34m[DEBUG] Intercepted response: ID=0x%X DLC=%d\033[0m\n", frame->id, frame->dlc);
}

/*---------------------------------------- Tests ----------------------------------------*/

// Encode/Decode roundtrip for SensorReq
void test_rpc_encode_decode_roundtrip() {
    printf("\n\033[33m====== Running: test_rpc_encode_decode_roundtrip ======\033[0m\n");

    bool pass = true;

    CanRpcSensorReq original = {
        .request_id = 0x12
    };

    CanFrame frame = can_encode_rpc_sensor_req(&original);
    printf("[DEBUG] Encoded frame ID=0x%X DLC=%d\n", frame.id, frame.dlc);

    pass &= (frame.id == ECU_RPC_GET_ID && frame.dlc == 3);

    CanRpcSensorReq decoded = can_decode_rpc_sensor_req(&frame);
    printf("[DEBUG] Decoded: request_id=0x%X\n", decoded.request_id);

    pass &= (decoded.request_id == original.request_id);

    VERIFY_TEST(pass);
}

// Encode/Decode roundtrip for SensorInformation
void test_rpc_response_roundtrip() {
    printf("\n\033[33m====== Running: test_rpc_response_roundtrip ======\033[0m\n");

    bool pass = true;

    CanRpcSensorInformation response = { .result = 0xA5 };
    CanFrame frame = can_encode_rpc_sensor_information(&response);

    pass &= (frame.id == ECU_RPC_GET_ID || frame.id == ECU_RPC_ANS_ID);

    CanRpcSensorInformation decoded = can_decode_rpc_sensor_information(&frame);
    pass &= (decoded.result == response.result);

    VERIFY_TEST(pass);
}

// Full end-to-end dispatch test
void test_rpc_dispatch_end_to_end() {
    printf("\n\033[33m====== Running: test_rpc_dispatch_end_to_end ======\033[0m\n");

    bool pass = true;
    got_response = false;

    ecu_rpc_client_init(); // <--- register handlers

    CanRpcSensorReq req = { .request_id = 0x01 };
    CanFrame frame = can_encode_rpc_sensor_req(&req);

    ecu_service_dispatch(&frame, mock_send);

    pass &= got_response;

    CanRpcSensorInformation decoded = can_decode_rpc_sensor_information(&intercepted_response);

    pass &= (intercepted_response.id == ECU_RPC_ANS_ID);
    pass &= (decoded.result == 0xA0);

    VERIFY_TEST(pass);
}


// Test: Invalid DLC
void test_rpc_invalid_dlc() {
    printf("\n\033[33m====== Running: test_rpc_invalid_dlc ======\033[0m\n");

    bool pass = true;

    CanFrame invalid = {0};
    invalid.id = ECU_RPC_GET_ID;
    invalid.dlc = 1;  // too short
    memset(invalid.data, 0, sizeof(invalid.data));

    got_response = false;
    ecu_service_dispatch(&invalid, mock_send);

    pass &= (!got_response);

    VERIFY_TEST(pass);
}

// Test: Invalid service and method IDs
void test_rpc_invalid_service_method() {
    printf("\n\033[33m====== Running: test_rpc_invalid_service_method ======\033[0m\n");

    bool pass = true;
    got_response = false;

    CanFrame req = {
        .id = ECU_RPC_GET_ID,
        .dlc = 3,
        .data = {0xFF, 0xFF, 0x00}  // service=0xFF, method=0xFF
    };

    ecu_service_dispatch(&req, mock_send);

    pass &= (!got_response);

    VERIFY_TEST(pass);
}

// Test: handler invocation
static bool handler_called = false;
void ecu_service_handle_mock(const CanFrame *req, CanFrame *resp) {
    handler_called = true;
    resp->id = ECU_RPC_ANS_ID;
}

void test_rpc_handler_invocation() {
    printf("\n\033[33m====== Running: test_rpc_handler_invocation ======\033[0m\n");

    bool pass = true;
    got_response = false;
    handler_called = false;

    CanRpcSensorReq req = { .request_id = 0x01 };
    CanFrame frame = can_encode_rpc_sensor_req(&req);

    ecu_service_dispatch(&frame, mock_send);

    pass &= got_response;
    pass &= (intercepted_response.id == ECU_RPC_ANS_ID);

    CanRpcSensorInformation decoded = can_decode_rpc_sensor_information(&intercepted_response);
    pass &= (decoded.result == 0xA0);

    VERIFY_TEST(pass);
}

/*---------------------------------------- Main ----------------------------------------*/

int main() {
    test_rpc_encode_decode_roundtrip();
    test_rpc_response_roundtrip();
    test_rpc_dispatch_end_to_end();
    test_rpc_invalid_dlc();
    test_rpc_invalid_service_method();
    test_rpc_handler_invocation();

    ASSERT_TESTS();
    return 0;
}
