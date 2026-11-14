#include "../../firmware_adapter/battery_service.h"
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

static bool read_fixture(void* unused, BatteryTelemetrySnapshot* snapshot) {
    (void)unused;
    memset(snapshot, 0, sizeof(*snapshot));
    snapshot->battery_pct = 81;
    snapshot->battery_health_available = true;
    snapshot->battery_health_pct = 97;
    snapshot->active_task_known = true;
    return true;
}

int main(void) {
    char input[256];
    char response[181];
    size_t length = 0;
    if(!fgets(input, sizeof(input), stdin)) return 1;
    BatteryService service;
    battery_service_init(&service);
    BatteryServiceGate gate = {0};
    gate.authenticated = true;
    gate.subscribed = true;
    gate.capability_agreed = true;
    gate.user_consented = true;
    gate.app_foreground = true;
    gate.session_epoch = 3;
    if(battery_service_handle(&service,
            (const uint8_t*)input, strlen(input), gate, 1000u,
            read_fixture, NULL, response, sizeof(response), &length)
            != BATTERY_SERVICE_OK || length == 0)
        return 2;
    if(fwrite(response, 1, length, stdout) != length) return 3;
    return 0;
}
