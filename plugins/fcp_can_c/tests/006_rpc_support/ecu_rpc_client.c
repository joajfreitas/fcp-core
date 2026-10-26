#include "ecu_rpc_client.h"
#include "generated_code/ecu_can_rpc.h"
#include "generated_code/ecu_can.h"

#include <string.h>
#include <stdbool.h>

/*---------------------------------------- RPC Client Functions ------------------------------------*/
static CANFrame rpc_response;

static void capture_response(const CANFrame *frame) {
    if (frame) rpc_response = *frame;
}

bool sensorservice_request_state(uint8_t *result) {
    if (!result) return false;

    CANRpcSensorReq request = {.request_id = 0x01};
    CANFrame frame = can_encode_rpc_request_state(&request);

    ecu_can_service_dispatch(&frame, capture_response);

    CANRpcSensorInformation response = can_decode_rpc_request_state_ans(&rpc_response);
    *result = response.result;

    return true;
}


/*---------------------------------------- Service Handlers ----------------------------------------*/

void ecu_can_service_handle_request_state(const CANFrame *req, CANFrame *resp) {
    if (!req || !resp) return;

    CANRpcSensorReq request = can_decode_rpc_request_state(req);
    CANRpcSensorInformation response = {0};

    switch (request.request_id) {
        case 0x01: response.result = 0xA0; break;
        case 0x02: response.result = 0xB0; break;
        case 0x11: response.result = 0xCD; break;
        default:   response.result = 0xFF; break;
    }

    *resp = can_encode_rpc_request_state_ans(&response);
    resp->sid = ECU_CAN_RPC_ANS_ID;
}

// SENSOR.GET_TEMPERATURE
void ecu_can_service_handle_get_temperature(const CANFrame *req, CANFrame *resp) {
    if (!req || !resp) return;

    CANRpcSensorReq request = can_decode_rpc_get_temperature(req);
    CANRpcTemperatureResponse response = {0};

    switch (request.request_id) {
        case 0x01: response.result = 22; break;
        case 0x02: response.result = 28; break;
        default:   response.result = 0xFF; break;
    }

    *resp = can_encode_rpc_get_temperature_ans(&response);
    resp->sid = ECU_CAN_RPC_ANS_ID;
}

/*---------------------------------------- RPC Registration (Example) ----------------------------------------*/

void can_ecu_rpc_client_init(void) {
    ecu_can_rpc_register(0, 0, ecu_can_service_handle_request_state);
    ecu_can_rpc_register(0, 1, ecu_can_service_handle_get_temperature);
}
