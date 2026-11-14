#include "battery_telemetry.h"

#include <inttypes.h>
#include <stdio.h>
#include <string.h>

BatteryTelemetryResult battery_telemetry_format(
    uint32_t request_id,
    const BatteryTelemetrySnapshot* snapshot,
    char* out,
    size_t capacity,
    size_t* written
) {
    if(written) *written = 0;
    if(out && capacity) out[0] = '\0';
    if(!snapshot || !out || !written || capacity == 0 || request_id == 0)
        return BATTERY_TELEMETRY_INVALID;
    if(snapshot->battery_pct < 0 || snapshot->battery_pct > 100 ||
       !snapshot->active_task_known ||
       (snapshot->battery_health_available &&
        (snapshot->battery_health_pct < 0 || snapshot->battery_health_pct > 100)) ||
       (snapshot->temperature_available &&
        (snapshot->temperature_tenths_c < -400 || snapshot->temperature_tenths_c > 1000)))
        return BATTERY_TELEMETRY_INVALID;

    char temp[BATTERY_TELEMETRY_MAX_FRAME + 1u];
    int n;
    if(snapshot->battery_health_available && snapshot->temperature_available) {
        n = snprintf(temp, sizeof(temp),
            "AI1|BAT_TELEM|%" PRIu32 "|v1,p=%d,h=%d,t=%d,c=%d,a=%d\n",
            request_id, snapshot->battery_pct, snapshot->battery_health_pct,
            snapshot->temperature_tenths_c,
            snapshot->charging ? 1 : 0, snapshot->active_task ? 1 : 0);
    } else if(snapshot->battery_health_available) {
        n = snprintf(temp, sizeof(temp),
            "AI1|BAT_TELEM|%" PRIu32 "|v1,p=%d,h=%d,c=%d,a=%d\n",
            request_id, snapshot->battery_pct, snapshot->battery_health_pct,
            snapshot->charging ? 1 : 0, snapshot->active_task ? 1 : 0);
    } else if(snapshot->temperature_available) {
        n = snprintf(temp, sizeof(temp),
            "AI1|BAT_TELEM|%" PRIu32 "|v1,p=%d,t=%d,c=%d,a=%d\n",
            request_id, snapshot->battery_pct, snapshot->temperature_tenths_c,
            snapshot->charging ? 1 : 0, snapshot->active_task ? 1 : 0);
    } else {
        n = snprintf(temp, sizeof(temp),
            "AI1|BAT_TELEM|%" PRIu32 "|v1,p=%d,c=%d,a=%d\n",
            request_id, snapshot->battery_pct,
            snapshot->charging ? 1 : 0, snapshot->active_task ? 1 : 0);
    }

    if(n < 0 || (size_t)n > BATTERY_TELEMETRY_MAX_FRAME)
        return BATTERY_TELEMETRY_NO_SPACE;
    if((size_t)n >= capacity)
        return BATTERY_TELEMETRY_NO_SPACE;
    memcpy(out, temp, (size_t)n + 1u);
    *written = (size_t)n;
    return BATTERY_TELEMETRY_OK;
}
