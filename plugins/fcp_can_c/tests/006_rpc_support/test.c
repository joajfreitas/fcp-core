#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "generated_code/can_frame.h"
#include "generated_code/ecu_can.h"

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

bool can_service_handle(CanServiceStruct *service) {
    printf("\033[34m[DEBUG] Handler received RPC request: service_id=%u, method_id=%u rpc_id=%u\033[0m\n",
            service->request->id.service_id,
            service->request->id.method_id,
            service->request->id.rpc_id);
    
    if (service->request->id.service_id == SENSOR_SERVICE_ID &&
        service->request->id.method_id == 0) {
        service->response->args[0] = 0xAB;
        printf("\033[34m[DEBUG] Handler responding with value: 0x%02X\033[0m\n", service->response->args[0]);
        return true;
    }
    
    return false;
}
    
void test_my_rpc_call() {

    printf("\n\033[33m====== Running: test_my_rpc_call ======\033[0m\n");

    uint8_t result;
    bool ok = call_my_rpc(&result);
    printf("\033[34m[DEBUG] Client received response value: 0x%02X\033[0m\n", result);
    VERIFY_TEST(ok && result == 0xAB);
}

void test_invalid_dlc() {

    printf("\n\033[33m====== Running: test_invalid_dlc ======\033[0m\n");

    CanFrame invalid_request;
    invalid_request.id = 0x123;                 // random
    invalid_request.dlc = 4;                    // invalid DLC
    memset(invalid_request.data, 0, sizeof(invalid_request.data));

    bool ok = can_service_dispatch(&invalid_request, NULL);
    if (!ok) {
        printf("\033[34m[DEBUG] Frame with invalid DLC correctly rejected.\033[0m\n");
    } else {
        printf("\033[34m[DEBUG] Frame with invalid DLC incorrectly accepted!\033[0m\n");
    }
    VERIFY_TEST(!ok);
}
    
// Static variable to store the response frame
static CanFrame response_frame;
static bool response_received = false;

// Callback function for handling the response
static void response_callback(const CanFrame *frame) {
    memcpy(&response_frame, frame, sizeof(CanFrame));
    response_received = true;
    printf("\033[34m[DEBUG] Response callback received frame with id: 0x%x\033[0m\n", frame->id);
}

void test_valid_dlc() {

    printf("\n\033[33m====== Running: test_valid_dlc ======\033[0m\n");

    response_received = false;

    CanFrame valid_request;
    valid_request.id = ECU_RPC_GET_ID;          // valid 
    valid_request.dlc = sizeof(RpcMessage);     // valid
    memset(valid_request.data, 0, sizeof(valid_request.data));

    RpcMessage *msg = (RpcMessage *) valid_request.data;
    msg->id.service_id = SENSOR_SERVICE_ID;
    msg->id.method_id = 0;

    bool ok = can_service_dispatch(&valid_request, response_callback);
    if (ok) {
        printf("\033[34m[DEBUG] Frame with valid DLC correctly accepted.\033[0m\n");
    } else {
        printf("\033[34m[DEBUG] Frame with valid DLC incorrectly rejected!\033[0m\n");
    }
    
    if (response_received) {
        RpcMessage *response = (RpcMessage *)response_frame.data;
        printf("\033[34m[DEBUG] Response value: 0x%02X\033[0m\n", response->args[0]);
        VERIFY_TEST(ok && response_received && response->args[0] == 0xAB);
    } else {
        printf("\033[31m[DEBUG] No response received from dispatch!\033[0m\n");
        VERIFY_TEST(ok && response_received);
    }
}

int main() {

    test_invalid_dlc();

    test_valid_dlc();

    test_my_rpc_call();

    ASSERT_TESTS();

    return 0;
}
