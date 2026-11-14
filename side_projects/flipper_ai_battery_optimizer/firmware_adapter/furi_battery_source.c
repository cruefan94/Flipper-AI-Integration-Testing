#include "furi_battery_source.h"

#include <furi_hal_power.h>
#include <string.h>

/**
 * Only the three Flipper battery functions already used by the main
 * Flipper AI project's local device-info view are referenced here.
 * Battery temperature is left unavailable without a verified Furi API.
 */
bool furi_battery_read_snapshot(void* context, BatteryTelemetrySnapshot* snapshot) {
    const FuriBatterySourceContext* state = context;
    if(!state || !snapshot || !state->active_task_known) return false;
    memset(snapshot, 0, sizeof(*snapshot));
    snapshot->battery_pct = (int)furi_hal_power_get_pct();
    snapshot->battery_health_available = true;
    snapshot->battery_health_pct = (int)furi_hal_power_get_bat_health_pct();
    snapshot->temperature_available = false;
    snapshot->charging = furi_hal_power_is_charging();
    snapshot->active_task_known = true;
    snapshot->active_task = state->active_task;
    return true;
}
