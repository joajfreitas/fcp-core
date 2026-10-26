#ifndef ECU_RPC_CLIENT_H
#define ECU_RPC_CLIENT_H

#include <stdint.h>
#include <stdbool.h>

#include "generated_code/ecu_can_rpc.h"
#include "generated_code/can_frame.h"
/*---------------------------------------- Client API ---------------------------------------------*/

/**
 * @brief Initializes and registers all RPC service handlers dynamically.
 * 
 * This function should be called once during ECU initialization to register
 * all handlers (e.g., RequestState, GetTemperature) with the RPC dispatcher.
 */
void can_ecu_rpc_client_init(void);

/**
 * @brief Requests the current sensor state from the ECU.
 * 
 * Sends an RPC request and receives the corresponding response.
 * 
 * @param[out] result Pointer to a variable that receives the sensor state.
 * @return true if successful, false otherwise.
 */
bool sensorservice_request_state(uint8_t *result);

/*---------------------------------------- Service Handlers ----------------------------------------*/

/**
 * @brief Handles a RequestState RPC request for the StateService.
 */
void can_ecu_service_handle_request_state(
    const CANFrame *req,
    CANFrame *resp
);

/**
 * @brief Handles a GetTemperature RPC request for the TemperatureService.
 */
void can_ecu_service_handle_get_temperature(
    const CANFrame *req,
    CANFrame *resp
);

#endif // ECU_RPC_CLIENT_H
