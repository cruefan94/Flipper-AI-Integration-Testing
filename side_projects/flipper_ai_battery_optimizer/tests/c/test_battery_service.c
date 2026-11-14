#include "../../firmware_adapter/battery_service.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    BatteryTelemetrySnapshot snapshot;
    int reads;
    bool available;
} FakePower;

static bool read_power(void* context, BatteryTelemetrySnapshot* out) {
    FakePower* fake = context;
    fake->reads++;
    if(!fake->available) return false;
    *out = fake->snapshot;
    return true;
}

static BatteryServiceGate trusted(uint64_t epoch) {
    BatteryServiceGate gate = {0};
    gate.authenticated = true;
    gate.subscribed = true;
    gate.capability_agreed = true;
    gate.user_consented = true;
    gate.app_foreground = true;
    gate.session_epoch = epoch;
    return gate;
}

static BatteryServiceResult handle(
    BatteryService* service, const char* input,
    BatteryServiceGate gate, uint64_t time_ms,
    FakePower* power, char* out, size_t capacity, size_t* written
) {
    return battery_service_handle(service, (const uint8_t*)input, strlen(input),
        gate, time_ms, read_power, power, out, capacity, written);
}

int main(void) {
    BatteryService service;
    battery_service_init(&service);
    FakePower power = {0};
    power.available = true;
    power.snapshot.battery_pct = 81;
    power.snapshot.battery_health_available = true;
    power.snapshot.battery_health_pct = 97;
    power.snapshot.active_task_known = true;
    char output[181] = {0};
    size_t written = 888u;
    BatteryServiceGate gate = trusted(4);

    gate.user_consented = false;
    assert(handle(&service, "AI1|BAT_GET|1|v1\n", gate, 1000, &power,
        output, sizeof(output), &written) == BATTERY_SERVICE_DENIED);
    assert(power.reads == 0 && written == 0);
    gate = trusted(4);
    gate.authenticated = false;
    assert(handle(&service, "AI1|BAT_GET|1|v1\n", gate, 1000, &power,
        output, sizeof(output), &written) == BATTERY_SERVICE_DENIED);
    assert(power.reads == 0);
    gate = trusted(4);
    gate.app_foreground = false;
    assert(handle(&service, "AI1|BAT_GET|1|v1\n", gate, 1000, &power,
        output, sizeof(output), &written) == BATTERY_SERVICE_DENIED);
    assert(power.reads == 0);

    gate = trusted(4);
    assert(handle(&service, "AI1|BAT_GET|1|v1\n", gate, 1000, &power,
        output, sizeof(output), &written) == BATTERY_SERVICE_OK);
    assert(strcmp(output, "AI1|BAT_TELEM|1|v1,p=81,h=97,c=0,a=0\n") == 0);
    assert(power.reads == 1 && written == strlen(output));

    assert(handle(&service, "AI1|BAT_GET|1|v1\n", gate, 1001, &power,
        output, sizeof(output), &written) == BATTERY_SERVICE_REPLAY);
    assert(power.reads == 1 && written == 0);
    assert(handle(&service, "AI1|BAT_GET|2|v1\n", gate, 1001, &power,
        output, sizeof(output), &written) == BATTERY_SERVICE_RATE_LIMITED);
    assert(power.reads == 1);
    assert(handle(&service, "AI1|BAT_GET|2|v1\n", gate,
        1000 + BATTERY_SERVICE_MIN_INTERVAL_MS - 1, &power,
        output, sizeof(output), &written) == BATTERY_SERVICE_RATE_LIMITED);
    assert(power.reads == 1);
    assert(handle(&service, "AI1|BAT_GET|2|v1\n", gate,
        1000 + BATTERY_SERVICE_MIN_INTERVAL_MS, &power,
        output, sizeof(output), &written) == BATTERY_SERVICE_OK);
    assert(power.reads == 2);

    power.snapshot.active_task = true;
    assert(handle(&service, "AI1|BAT_GET|3|v1\n", gate,
        1000 + BATTERY_SERVICE_MIN_INTERVAL_MS * 2, &power,
        output, sizeof(output), &written) == BATTERY_SERVICE_HARDWARE_BUSY);
    assert(written == 0);
    power.snapshot.active_task = false;
    power.snapshot.active_task_known = false;
    assert(handle(&service, "AI1|BAT_GET|3|v1\n", gate,
        1000 + BATTERY_SERVICE_MIN_INTERVAL_MS * 2, &power,
        output, sizeof(output), &written) == BATTERY_SERVICE_READ_UNAVAILABLE);
    power.snapshot.active_task_known = true;
    power.available = false;
    assert(handle(&service, "AI1|BAT_GET|3|v1\n", gate,
        1000 + BATTERY_SERVICE_MIN_INTERVAL_MS * 2, &power,
        output, sizeof(output), &written) == BATTERY_SERVICE_READ_UNAVAILABLE);
    power.available = true;

    assert(handle(&service, "AI1|BAT_GET|3|v1\n", gate,
        1000 + BATTERY_SERVICE_MIN_INTERVAL_MS * 2, &power,
        output, 5, &written) == BATTERY_SERVICE_NO_SPACE);
    assert(written == 0);
    assert(handle(&service, "AI1|BAT_GET|3|v1\n", gate,
        1000 + BATTERY_SERVICE_MIN_INTERVAL_MS * 2, &power,
        output, sizeof(output), &written) == BATTERY_SERVICE_OK);

    int before = power.reads;
    assert(handle(&service, "AI1|ASK|4|v1\n", gate,
        1000 + BATTERY_SERVICE_MIN_INTERVAL_MS * 3, &power,
        output, sizeof(output), &written) == BATTERY_SERVICE_BAD_FRAME);
    assert(power.reads == before);

    gate = trusted(5); /* new connection epoch */
    assert(handle(&service, "AI1|BAT_GET|1|v1\n", gate, 1, &power,
        output, sizeof(output), &written) == BATTERY_SERVICE_OK);
    assert(power.reads == before + 1);

    battery_service_reset(&service);
    assert(!service.initialized && !service.responded);
    puts("PASS BatteryServiceTest (read-only gate, epoch, anti-replay, rate-limit)");
    return 0;
}
