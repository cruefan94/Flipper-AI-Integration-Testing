#include "../../firmware_adapter/furi_battery_source.h"
#include <assert.h>
#include <stdio.h>

static int pct_calls;
static int health_calls;
static int charge_calls;
static unsigned pct = 73u;
static unsigned health = 92u;
static bool charging = false;

uint8_t furi_hal_power_get_pct(void) { pct_calls++; return (uint8_t)pct; }
uint8_t furi_hal_power_get_bat_health_pct(void) {
    health_calls++;
    return (uint8_t)health;
}
bool furi_hal_power_is_charging(void) { charge_calls++; return charging; }

int main(void) {
    BatteryTelemetrySnapshot sample = {0};
    FuriBatterySourceContext ctx = {0};
    assert(!furi_battery_read_snapshot(&ctx, &sample));
    assert(pct_calls == 0); /* never poll without authoritative task status */
    ctx.active_task_known = true;
    ctx.active_task = false;
    assert(furi_battery_read_snapshot(&ctx, &sample));
    assert(sample.battery_pct == 73 && sample.battery_health_pct == 92);
    assert(sample.battery_health_available && !sample.temperature_available);
    assert(!sample.charging && sample.active_task_known && !sample.active_task);
    assert(pct_calls == 1 && health_calls == 1 && charge_calls == 1);

    ctx.active_task = true;
    charging = true;
    assert(furi_battery_read_snapshot(&ctx, &sample));
    assert(sample.active_task && sample.charging);
    assert(pct_calls == 2 && health_calls == 2 && charge_calls == 2);

    assert(!furi_battery_read_snapshot(NULL, &sample));
    assert(!furi_battery_read_snapshot(&ctx, NULL));
    assert(pct_calls == 2);
    puts("PASS FuriBatterySourceTest (mock HAL only; no real hardware)");
    return 0;
}
