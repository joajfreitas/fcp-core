#ifndef ECU_RPC_CLIENT_H
#define ECU_RPC_CLIENT_H

#include <stdint.h>
#include <stdbool.h>

#include "generated_code/ecu_rpc.h"
#include "generated_code/can_frame.h"  // Include CanFrame definition

// Function to request sensor state
bool sensorservice_request_state(uint8_t *result);

/* Handlers for services using raw CAN frames */
void ecu_service_handle_request_state(
    const CanFrame *req,
    CanFrame *resp
);

void ecu_service_handle_get_temperature(
    const CanFrame *req,
    CanFrame *resp
);

#endif // ECU_RPC_CLIENT_H
