#include "battery_service.h"
#include "battery_request.h"
#include <string.h>

void battery_service_init(BatteryService* service) {
    if(service) memset(service, 0, sizeof(*service));
}

void battery_service_reset(BatteryService* service) {
    battery_service_init(service);
}

BatteryServiceResult battery_service_handle(
    BatteryService* service,
    const uint8_t* frame,
    size_t frame_length,
    BatteryServiceGate gate,
    uint64_t now_ms,
    BatteryServiceReadSnapshot read_snapshot,
    void* snapshot_context,
    char* response,
    size_t response_capacity,
    size_t* response_length
) {
    if(response_length) *response_length = 0;
    if(response && response_capacity) response[0] = '\0';
    if(!service || !response || !response_length || !read_snapshot ||
       response_capacity == 0 || gate.session_epoch == 0)
        return BATTERY_SERVICE_DENIED;
    if(!gate.authenticated || !gate.subscribed || !gate.capability_agreed ||
       !gate.user_consented || !gate.app_foreground)
        return BATTERY_SERVICE_DENIED;

    uint32_t request_id = 0;
    if(battery_request_parse(frame, frame_length,
            gate.authenticated, gate.subscribed, gate.capability_agreed,
            &request_id) != BATTERY_REQUEST_OK)
        return BATTERY_SERVICE_BAD_FRAME;

    if(service->initialized && service->session_epoch != gate.session_epoch) {
        /* Each trusted generation starts a fresh request counter. */
        battery_service_reset(service);
    }
    if(!service->initialized) {
        service->initialized = true;
        service->session_epoch = gate.session_epoch;
    }

    if(service->responded && request_id <= service->last_request_id)
        return BATTERY_SERVICE_REPLAY;
    if(service->responded) {
        if(now_ms < service->last_response_at_ms)
            return BATTERY_SERVICE_RATE_LIMITED;
        if(now_ms - service->last_response_at_ms < BATTERY_SERVICE_MIN_INTERVAL_MS)
            return BATTERY_SERVICE_RATE_LIMITED;
    }

    BatteryTelemetrySnapshot snapshot = {0};
    if(!read_snapshot(snapshot_context, &snapshot))
        return BATTERY_SERVICE_READ_UNAVAILABLE;
    if(!snapshot.active_task_known)
        return BATTERY_SERVICE_READ_UNAVAILABLE;
    if(snapshot.active_task)
        return BATTERY_SERVICE_HARDWARE_BUSY;

    if(battery_telemetry_format(request_id, &snapshot,
            response, response_capacity, response_length) != BATTERY_TELEMETRY_OK)
        return BATTERY_SERVICE_NO_SPACE;

    service->responded = true;
    service->last_request_id = request_id;
    service->last_response_at_ms = now_ms;
    return BATTERY_SERVICE_OK;
}
