#include "generated_code/ecu_can.h"
#include "generated_code/ecu_rpc.h"
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

/*------------------- RPC Encode/Decode Tests -------------------*/
void test_rpc_sensor_information() {
    CanRpcSensorInformation msg = {
        .result = 0xA5
    };

    // Encode
    CanFrame frame = can_encode_rpc_sensor_information(&msg);
    printf("Encoded frame ID: 0x%X, DLC: %d\n", frame.id, frame.dlc);

    VERIFY_TEST(frame.id == ECU_RPC_GET_ID || frame.id == ECU_RPC_ANS_ID);

    // Decode
    CanRpcSensorInformation decoded = can_decode_rpc_sensor_information(&frame);
    VERIFY_TEST(decoded.result == msg.result);
}

void test_rpc_sensor_request() {
    CanRpcSensorReq msg = {
        .request_id = 0x01
    };

    // Encode
    CanFrame frame = can_encode_rpc_sensor_req(&msg);
    VERIFY_TEST(frame.id == ECU_RPC_GET_ID || frame.id == ECU_RPC_ANS_ID);

    // Decode
    CanRpcSensorReq decoded = can_decode_rpc_sensor_req(&frame);
    VERIFY_TEST(decoded.request_id == msg.request_id);
}

void test_rpc_temperature_response() {
    CanRpcTemperatureResponse msg = {
        .result = 25
    };

    // Encode
    CanFrame frame = can_encode_rpc_temperature_response(&msg);
    VERIFY_TEST(frame.id == ECU_RPC_GET_ID || frame.id == ECU_RPC_ANS_ID);

    // Decode
    CanRpcTemperatureResponse decoded = can_decode_rpc_temperature_response(&frame);
    VERIFY_TEST(decoded.result == msg.result);
}

/*------------------- Main -------------------*/
int main() {
    test_rpc_sensor_information();
    test_rpc_sensor_request();
    test_rpc_temperature_response();

    ASSERT_TESTS();
    return 0;
}
