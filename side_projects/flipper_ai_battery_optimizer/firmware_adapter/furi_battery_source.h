#ifndef FLIPPER_AI_FURI_BATTERY_SOURCE_H
#define FLIPPER_AI_FURI_BATTERY_SOURCE_H

#include "battery_telemetry.h"
#include <stdbool.h>

/**
 * Momentum/Furi HAL bridge for the separate battery optimizer.
 * Future integration adapter ONLY: it does not register a BLE endpoint.
 *
 * The host must authoritatively supply hardware-busy status; if that status
 * is unknown, the provider rejects the read rather than claiming idle.
 */
typedef struct {
    bool active_task_known;
    bool active_task;
} FuriBatterySourceContext;

bool furi_battery_read_snapshot(void* context, BatteryTelemetrySnapshot* snapshot);

#endif
