#include "../../firmware_adapter/furi_battery_source.h"
#include "../../firmware_adapter/battery_service.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static unsigned reads;
uint8_t furi_hal_power_get_pct(void) { reads++; return 66u; }
uint8_t furi_hal_power_get_bat_health_pct(void) { return 93u; }
bool furi_hal_power_is_charging(void) { return false; }

int main(void) {
    BatteryService service;
    battery_service_init(&service);
    BatteryServiceGate gate = {0};
    gate.authenticated = true;
    gate.subscribed = true;
    gate.capability_agreed = true;
    gate.user_consented = true;
    gate.app_foreground = true;
    gate.session_epoch = 3u;

    FuriBatterySourceContext context = {0};
    char output[181];
    size_t length = 0;
    const char* request = "AI1|BAT_GET|9|v1\n";
    assert(battery_service_handle(&service, (const uint8_t*)request, strlen(request),
        gate, 1000u, furi_battery_read_snapshot, &context, output,
        sizeof(output), &length) == BATTERY_SERVICE_READ_UNAVAILABLE);
    assert(reads == 0);

    context.active_task_known = true;
    context.active_task = true;
    assert(battery_service_handle(&service, (const uint8_t*)request, strlen(request),
        gate, 1000u, furi_battery_read_snapshot, &context, output,
        sizeof(output), &length) == BATTERY_SERVICE_HARDWARE_BUSY);
    assert(length == 0);

    context.active_task = false;
    assert(battery_service_handle(&service, (const uint8_t*)request, strlen(request),
        gate, 1000u, furi_battery_read_snapshot, &context, output,
        sizeof(output), &length) == BATTERY_SERVICE_OK);
    assert(strcmp(output, "AI1|BAT_TELEM|9|v1,p=66,h=93,c=0,a=0\n") == 0);
    assert(reads == 2); /* busy+idle; unknown was blocked */
    puts("PASS FuriServiceIntegrationTest (mock HAL -> C service -> wire)");
    return 0;
}
