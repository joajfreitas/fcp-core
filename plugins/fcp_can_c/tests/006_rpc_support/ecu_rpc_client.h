#ifndef ECU_RPC_CLIENT_H
#define ECU_RPC_CLIENT_H

#include <stdbool.h>
#include <stdint.h>

#include "generated_code/ecu_rpc.h"
#include "generated_code/can_frame.h"

#define SENSOR_SERVICE_ID 1

/* SensorService RPC Methods */
bool request_sensor_state(uint8_t *result);

/* Dispatch function to handle CAN RPC requests */
void can_service_dispatch(const CanFrame *request, void (*response_callback)(const CanFrame *));

/* For test compatibility */
#define CALL_MY_RPC REQUEST_SENSOR_STATE

#endif // ECU_RPC_CLIENT_H
