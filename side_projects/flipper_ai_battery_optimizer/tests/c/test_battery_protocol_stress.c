#include "../../firmware_adapter/battery_request.h"
#include "../../firmware_adapter/battery_telemetry.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

/* Stable pseudo-random test corpus; not a hardware test or security proof. */
static uint32_t state = UINT32_C(0x7A45B217);
static uint32_t next_random(void) {
    state ^= state << 13u;
    state ^= state >> 17u;
    state ^= state << 5u;
    return state;
}

int main(void) {
    uint8_t buffer[260];
    for(unsigned i = 0; i < 20000u; i++) {
        size_t length = (size_t)(next_random() % sizeof(buffer));
        for(size_t j = 0; j < length; j++)
            buffer[j] = (uint8_t)(next_random() & 0xFFu);
        uint32_t id = 123u;
        BatteryRequestResult result = battery_request_parse(
            buffer, length, true, true, true, &id);
        if(result == BATTERY_REQUEST_OK) {
            assert(length >= 17u && length <= 180u);
            assert(id > 0);
        } else {
            assert(id == 0);
        }
    }
    BatteryTelemetrySnapshot snapshot = {0};
    snapshot.active_task_known = true;
    for(unsigned i = 0; i < 10000u; i++) {
        char output[181] = {0};
        size_t written = 999u;
        snapshot.battery_pct = (int)(next_random() % 150u) - 20;
        snapshot.battery_health_available = (next_random() & 1u) != 0;
        snapshot.battery_health_pct = (int)(next_random() % 150u) - 20;
        snapshot.temperature_available = (next_random() & 1u) != 0;
        snapshot.temperature_tenths_c = (int)(next_random() % 1600u) - 500;
        snapshot.charging = (next_random() & 1u) != 0;
        snapshot.active_task = (next_random() & 1u) != 0;
        BatteryTelemetryResult result = battery_telemetry_format(
            7u, &snapshot, output, sizeof(output), &written);
        if(result == BATTERY_TELEMETRY_OK) {
            assert(written > 0 && written <= 180u);
            assert(strlen(output) == written);
            assert(strncmp(output, "AI1|BAT_TELEM|7|v1,", 18u) == 0);
            assert(output[written-1] == '\n');
        } else {
            assert(written == 0);
        }
    }
    puts("PASS BatteryProtocolStressTest (30000 deterministic malformed/bounded cases)");
    return 0;
}
