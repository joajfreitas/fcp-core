#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

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
    printf("\033[0m");      \
    if (all_tests_passed) { \
        exit(EXIT_SUCCESS); \
    } else {                \
        exit(EXIT_FAILURE); \
    }

bool can_service_handle(CanServiceStruct *service) {
    printf("\033[34m[DEBUG] Handler received RPC request: service_id=%u, method_id=%u (rpc_id=%u)\033[0m\n",
            service->request->id.service_id,
            service->request->id.method_id,
            service->request->id.rpc_id);
    
    if (service->request->id.rpc_id == 0) {
        service->response->args[0] = 0xAB;
        printf("\033[34m[DEBUG] Handler responding with value: 0x%02X\033[0m\n", service->response->args[0]);
        return true;
    }
    
    return false;
}
    
void test_my_rpc_call() {
    uint8_t result;
    bool ok = call_my_rpc(&result);
    printf("\033[34m[DEBUG] Client received response value: 0x%02X\033[0m\n", result);
    VERIFY_TEST(ok && result == 0xAB);
}

    
int main() {
    
    test_my_rpc_call();

    ASSERT_TESTS();

    return 0;
}
