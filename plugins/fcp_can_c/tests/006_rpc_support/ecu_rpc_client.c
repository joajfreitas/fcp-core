#include "ecu_rpc_client.h"
#include "generated_code/ecu_rpc.h"
#include "generated_code/ecu_can.h"

#include <string.h>
#include <stdbool.h>

static CanFrame rpc_response;
static void capture_response(const CanFrame *frame) {
    rpc_response = *frame;
}

// Wrapper for sending a request and capturing response
bool sensorservice_request_state(uint8_t *result) {
    CanRpcSensorReq request = {
        .id = { .service_id = 0, .method_id = 0 },
        .request_id = 0x01
    };

    CanFrame frame = can_encode_rpc_sensor_req(&request);
    ecu_service_dispatch(&frame, capture_response);

    CanRpcSensorInformation response = can_decode_rpc_sensor_information(&rpc_response);
    *result = response.result;

    return true;
}

/* ===== Service Handlers ===== */

// Handler for SENSOR REQUEST STATE
void ecu_service_handle_request_state(const CanFrame *req, CanFrame *resp) {
    if (!req || !resp) return;

    // Decode request
    CanRpcSensorReq request = can_decode_rpc_sensor_req(req);

    // Prepare response structure
    CanRpcSensorInformation response = {0};

    switch (request.request_id) {
        case 0x01: response.result = 0xA0; break;
        case 0x02: response.result = 0xB0; break;
        case 0x11: response.result = 0xCD; break;
        default:   response.result = 0xFF; break;
    }

    // Encode response frame
    *resp = can_encode_rpc_sensor_information(&response);
    resp->id = ECU_RPC_ANS_ID; // ensure correct answer ID
}

// Handler for GET TEMPERATURE
void ecu_service_handle_get_temperature(const CanFrame *req, CanFrame *resp) {
    if (!req || !resp) return;

    CanRpcSensorReq request = can_decode_rpc_sensor_req(req);
    CanRpcTemperatureResponse response = {0};

    switch (request.request_id) {
        case 0x01: response.result = 22; break;
        case 0x02: response.result = 28; break;
        default:   response.result = 0xFF; break;
    }

    *resp = can_encode_rpc_temperature_response(&response);
    resp->id = ECU_RPC_ANS_ID;
}
