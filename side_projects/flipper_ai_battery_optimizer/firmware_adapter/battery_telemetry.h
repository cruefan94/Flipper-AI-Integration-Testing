#ifndef FLIPPER_BATTERY_TELEMETRY_H
#define FLIPPER_BATTERY_TELEMETRY_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Independent portable C source. No BLE, HAL, network, or hardware mutation.
 * Proposed AI1 BAT_TELEM v1 wire frame, NOT registered in Momentum firmware.
 */
#define BATTERY_TELEMETRY_MAX_FRAME 180u

typedef struct {
    int battery_pct;                /* 0..100 */
    bool battery_health_available;
    int battery_health_pct;         /* 0..100 when available */
    bool temperature_available;
    int temperature_tenths_c;       /* -400..1000 when available */
    bool charging;
    bool active_task_known;         /* caller must verify; no invented idle flag */
    bool active_task;
} BatteryTelemetrySnapshot;

typedef enum {
    BATTERY_TELEMETRY_OK = 0,
    BATTERY_TELEMETRY_INVALID,
    BATTERY_TELEMETRY_NO_SPACE
} BatteryTelemetryResult;

/* Formats one bounded ASCII AI1 response, no GATT send or request handling.
 * Requires authenticated session / consent / matched request separately.
 * On failure, written=0 and output starts with NUL when writable.
 */
BatteryTelemetryResult battery_telemetry_format(
    uint32_t request_id,
    const BatteryTelemetrySnapshot* snapshot,
    char* out,
    size_t capacity,
    size_t* written
);
#endif
