#include "ecu_rpc_client.h"

#include "generated_code/ecu_rpc.h"
#include "generated_code/ecu_can.h"

#include <string.h>
#include <stdbool.h>

static CanFrame rpc_response;

static void capture_response(const CanFrame *frame) {
    memcpy(&rpc_response, frame, sizeof(CanFrame));
}

bool request_sensor_state(uint8_t *result) { //sensorservice_requeststate
    CanFrame request;
    request.id = ECU_RPC_GET_ID;
    request.dlc = 8;

    RpcMessage *msg = (RpcMessage *) request.data;
    msg->rpc_get_id = ECU_RPC_GET_ID;
    msg->rpc_ans_id = ECU_RPC_ANS_ID;
    memset(&msg->payload, 0, sizeof(RpcPayload));

    /* Add the can_service_dispatch function declaration from can_service.h */
    can_service_dispatch(&request, capture_response);

    RpcMessage *res = (RpcMessage *) rpc_response.data;
    *result = res->payload.sensorservice_requeststate_res.result;
    return true;
}
