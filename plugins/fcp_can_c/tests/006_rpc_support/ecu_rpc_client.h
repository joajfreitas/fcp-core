#ifndef ECU_RPC_CLIENT_H
#define ECU_RPC_CLIENT_H

#include <stdint.h>
#include <stdbool.h>

#include "generated_code/ecu_rpc.h"
#include "generated_code/can_frame.h"

bool sensorservice_requeststate(uint8_t *result);

/* Handlers for services */
void ecu_service_handle_requeststate(
    const CanRpcSensorReq *request,
    CanRpcSensorInformation *response
);

void ecu_service_handle_gettemperature(
    const CanRpcSensorReq *request,
    CanRpcTemperatureResponse *response
);

#endif // ECU_RPC_CLIENT_H
