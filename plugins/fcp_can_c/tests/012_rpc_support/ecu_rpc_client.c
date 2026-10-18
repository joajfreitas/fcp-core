#include "ecu_rpc_client.h"
#include "generated_code/ecu_rpc.h"
#include "generated_code/ecu_can.h"

#include <string.h>
#include <stdbool.h>

/*---------------------------------------- RPC Client Functions ------------------------------------*/
static CanFrame rpc_response;

static void capture_response(const CanFrame *frame) {
    if (frame) rpc_response = *frame;
}

bool sensorservice_request_state(uint8_t *result) {
    if (!result) return false;

    CanRpcSensorReq request = {.request_id = 0x01};
    CanFrame frame = can2b_encode_rpc_request_state(&request);

    ecu_service_dispatch(&frame, capture_response);

    CanRpcSensorInformation response = can2b_decode_rpc_request_state_ans(&rpc_response);
    *result = response.result;

    return true;
}


/*---------------------------------------- Service Handlers ----------------------------------------*/

void ecu_can2b_service_handle_request_state(const CanFrame *req, CanFrame *resp) {
    if (!req || !resp) return;

    CanRpcSensorReq request = can2b_decode_rpc_request_state(req);
    CanRpcSensorInformation response = {0};

    switch (request.request_id) {
        case 0x01: response.result = 0xA0; break;
        case 0x02: response.result = 0xB0; break;
        case 0x11: response.result = 0xCD; break;
        default:   response.result = 0xFF; break;
    }

    *resp = can2b_encode_rpc_request_state_ans(&response);
    resp->ide = 1;
    resp->sid = ECU_CAN2B_RPC_ANS_ID & 0x03FF;
    resp->eid = (ECU_CAN2B_RPC_ANS_ID >> 11) & 0x07FFFF;
}

// SENSOR.GET_TEMPERATURE
void ecu_can2b_service_handle_get_temperature(const CanFrame *req, CanFrame *resp) {
    if (!req || !resp) return;

    CanRpcSensorReq request = can2b_decode_rpc_get_temperature(req);
    CanRpcTemperatureResponse response = {0};

    switch (request.request_id) {
        case 0x01: response.result = 22; break;
        case 0x02: response.result = 28; break;
        default:   response.result = 0xFF; break;
    }

    *resp = can2b_encode_rpc_get_temperature_ans(&response);
    resp->ide = 1;
    resp->sid = ECU_CAN2B_RPC_ANS_ID & 0x03FF;
    resp->eid = (ECU_CAN2B_RPC_ANS_ID >> 11) & 0x07FFFF;
}

/*---------------------------------------- RPC Registration (Example) ----------------------------------------*/

void ecu_rpc_client_init(void) {
    ecu_rpc_register(0, 0, ecu_can2b_service_handle_request_state);
    ecu_rpc_register(0, 1, ecu_can2b_service_handle_get_temperature);
}
