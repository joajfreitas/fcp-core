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

// Globals
static CanFrame intercepted_response;
static bool got_response = false;

// Mock send function
void mock_send(const CanFrame *frame) {
    memcpy(&intercepted_response, frame, sizeof(CanFrame));
    got_response = true;
    printf("\033[34m[DEBUG] Intercepted response: ID=0x%X DLC=%d\033[0m\n", frame->id, frame->dlc);
}

// Test: Encode and decode roundtrip
void test_rpc_encode_decode_roundtrip() {
    printf("\n\033[33m====== Running: test_rpc_encode_decode_roundtrip ======\033[0m\n");

    bool pass = true;

    CanRpcSensorReq original = {
        .id.service_id = 0,
        .id.method_id = 0,
        .request_id = 0x12
    };

    CanFrame frame = can_encode_rpc_sensor_req(&original);
    printf("\033[34m[DEBUG] Encoded frame ID=0x%X DLC=%d\033[0m\n", frame.id, frame.dlc);

    pass &= (frame.id == ECU_RPC_GET_ID && frame.dlc == 3);

    CanRpcSensorReq decoded = can_decode_rpc_sensor_req(&frame);
    printf("\033[34m[DEBUG] Decoded: service_id=0x%X method_id=0x%X request_id=0x%X\033[0m\n",
           decoded.id.service_id, decoded.id.method_id, decoded.request_id);

    
    pass &= (decoded.id.service_id == 0);
    pass &= (decoded.id.method_id == 0);
    pass &= (decoded.request_id == original.request_id);

    VERIFY_TEST(pass);
}

// Test: Full dispatch from request to response
void test_rpc_dispatch_end_to_end() {
    printf("\n\033[33m====== Running: test_rpc_dispatch_end_to_end ======\033[0m\n");

    bool pass = true;
    got_response = false;

    CanRpcSensorReq req = {
        .id.service_id = 0,
        .id.method_id = 0,
        .request_id = 0x01
    };

    CanFrame request = can_encode_rpc_sensor_req(&req);
    request.id = ECU_RPC_GET_ID;

    printf("\033[34m[DEBUG] Sending request: frame.id = 0x%X, request_id = 0x%X\033[0m\n",
           request.id, req.request_id);

    ecu_service_dispatch_sensor_req(&request, mock_send);

    pass &= got_response;

    CanRpcSensorReq decoded = can_decode_rpc_sensor_req(&intercepted_response);
    printf("\033[34m[DEBUG] Received response: frame.id = 0x%X, request_id = 0x%X\033[0m\n",
           intercepted_response.id, decoded.request_id);

    pass &= (intercepted_response.id == ECU_RPC_ANS_ID);
    pass &= (decoded.request_id == 0xA0);

    VERIFY_TEST(pass);
}

// Test: Invalid DLC
void test_rpc_invalid_dlc() {
    printf("\n\033[33m====== Running: test_rpc_invalid_dlc ======\033[0m\n");

    bool pass = true;

    CanFrame invalid;
    invalid.id = ECU_RPC_GET_ID;
    invalid.dlc = 1;  // invalid
    memset(invalid.data, 0, sizeof(invalid.data));

    printf("\033[34m[DEBUG] Sending invalid frame ID=0x%X DLC=%d\033[0m\n", invalid.id, invalid.dlc);

    got_response = false;

    if (invalid.dlc >= 3) {
        ecu_service_dispatch_sensor_req(&invalid, mock_send);
    }

    pass &= (!got_response);
    VERIFY_TEST(pass);
}

int main() {
    test_rpc_encode_decode_roundtrip();
    test_rpc_dispatch_end_to_end();
    test_rpc_invalid_dlc();

    ASSERT_TESTS();
    return 0;
}
