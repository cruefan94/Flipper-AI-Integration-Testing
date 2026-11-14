#ifndef FLIPPER_BATTERY_SERVICE_H
#define FLIPPER_BATTERY_SERVICE_H

#include "battery_telemetry.h"
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Portable, read-only BAT_GET -> BAT_TELEM bridge.
 * Neither Bluetooth nor Momentum HAL calls exist here.
 * The host must supply authentication and epoch from its trusted BLE service.
 * Only the host may register the request handler, after explicit approval.
 */
#define BATTERY_SERVICE_MIN_INTERVAL_MS UINT64_C(180000)

typedef struct {
    bool authenticated;
    bool subscribed;
    bool capability_agreed;
    bool user_consented;
    bool app_foreground;
    uint64_t session_epoch;
} BatteryServiceGate;

typedef struct {
    bool initialized;
    uint64_t session_epoch;
    bool responded;
    uint32_t last_request_id;
    uint64_t last_response_at_ms;
} BatteryService;

typedef bool (*BatteryServiceReadSnapshot)(void* context, BatteryTelemetrySnapshot* snapshot);

typedef enum {
    BATTERY_SERVICE_OK = 0,
    BATTERY_SERVICE_DENIED,
    BATTERY_SERVICE_BAD_FRAME,
    BATTERY_SERVICE_REPLAY,
    BATTERY_SERVICE_RATE_LIMITED,
    BATTERY_SERVICE_READ_UNAVAILABLE,
    BATTERY_SERVICE_HARDWARE_BUSY,
    BATTERY_SERVICE_NO_SPACE
} BatteryServiceResult;

void battery_service_init(BatteryService* service);
void battery_service_reset(BatteryService* service);

/* Returns one response frame, or no data. Never changes device settings.
 * Battery reads occur at most once per authorized, rate-limited request.
 * A failed response never consumes the rate-limit quota.
 */
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
);
#endif
