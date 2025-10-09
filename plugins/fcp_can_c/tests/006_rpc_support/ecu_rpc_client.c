#include "ecu_rpc_client.h"

#include "generated_code/ecu_rpc.h"
#include "generated_code/ecu_can.h"

#include <string.h>
#include <stdbool.h>

static CanFrame rpc_response;

static void capture_response(const CanFrame *frame) {
    rpc_response = *frame;
}

bool sensorservice_requeststate(uint8_t *result) {
    CanRpcSensorReq original = {
        .id = { .service_id = 0, .method_id = 0 },
        .request_id = 0x12
    };

    CanFrame request = can_encode_rpc_sensor_req(&original);

    ecu_service_dispatch_sensor_req(&request, capture_response);

    CanRpcSensorInformation response = can_decode_rpc_sensor_information(&rpc_response);
    *result = response.result;

    return true;
}


// Handler for ECU_REQUESTSTATE
void ecu_service_handle_requeststate(
    const CanRpcSensorReq *request,
    CanRpcSensorInformation *response
) {
    switch (request->request_id) {
        case 0x01:
            response->result = 0xA0;
            break;
        case 0x02:
            response->result = 0xB0;
            break;
        case 0x11:
            response->result = 0xCD;
            break;
        default:
            response->result = 0xFF;
            break;
    }
}

// Handler for ECU_GETTEMPERATURE
void ecu_service_handle_gettemperature(
    const CanRpcSensorReq *request,
    CanRpcTemperatureResponse *response
) {
    switch (request->request_id) {
        case 0x01:
            response->result = 22;
            break;
        case 0x02:
            response->result = 28;
            break;
        default:
            response->result = 0xFF;
            break;
    }
}
