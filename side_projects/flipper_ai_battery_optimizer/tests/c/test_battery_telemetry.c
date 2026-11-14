#include "../../firmware_adapter/battery_telemetry.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static BatteryTelemetrySnapshot fixture(void) {
    BatteryTelemetrySnapshot s = {0};
    s.battery_pct = 83;
    s.battery_health_available = true;
    s.battery_health_pct = 95;
    s.temperature_available = true;
    s.temperature_tenths_c = 230;
    s.charging = false;
    s.active_task_known = true;
    s.active_task = false;
    return s;
}

int main(void) {
    char frame[181];
    size_t written = 999u;
    BatteryTelemetrySnapshot snapshot = fixture();
    const char* expected =
        "AI1|BAT_TELEM|7|v1,p=83,h=95,t=230,c=0,a=0\n";
    assert(battery_telemetry_format(7u, &snapshot, frame, sizeof(frame), &written)
           == BATTERY_TELEMETRY_OK);
    assert(strcmp(frame, expected) == 0);
    assert(written == strlen(expected));
    assert(written <= BATTERY_TELEMETRY_MAX_FRAME);

    assert(battery_telemetry_format(7u, &snapshot, frame, written, &written)
           == BATTERY_TELEMETRY_NO_SPACE);
    assert(written == 0 && frame[0] == '\0');

    snapshot.temperature_available = false;
    assert(battery_telemetry_format(7u, &snapshot, frame, sizeof(frame), &written)
           == BATTERY_TELEMETRY_OK);
    assert(strcmp(frame, "AI1|BAT_TELEM|7|v1,p=83,h=95,c=0,a=0\n") == 0);

    snapshot.battery_health_available = false;
    assert(battery_telemetry_format(7u, &snapshot, frame, sizeof(frame), &written)
           == BATTERY_TELEMETRY_OK);
    assert(strcmp(frame, "AI1|BAT_TELEM|7|v1,p=83,c=0,a=0\n") == 0);

    snapshot.temperature_available = true;
    snapshot.temperature_tenths_c = -100;
    snapshot.charging = true;
    snapshot.active_task = true;
    assert(battery_telemetry_format(4294967295u, &snapshot, frame, sizeof(frame), &written)
           == BATTERY_TELEMETRY_OK);
    assert(strcmp(frame,
        "AI1|BAT_TELEM|4294967295|v1,p=83,t=-100,c=1,a=1\n") == 0);

    assert(battery_telemetry_format(0, &snapshot, frame, sizeof(frame), &written)
           == BATTERY_TELEMETRY_INVALID);
    assert(frame[0] == '\0' && written == 0);

    snapshot.active_task_known = false;
    assert(battery_telemetry_format(9, &snapshot, frame, sizeof(frame), &written)
           == BATTERY_TELEMETRY_INVALID);
    snapshot.active_task_known = true;

    snapshot.battery_pct = -1;
    assert(battery_telemetry_format(9, &snapshot, frame, sizeof(frame), &written)
           == BATTERY_TELEMETRY_INVALID);
    snapshot.battery_pct = 101;
    assert(battery_telemetry_format(9, &snapshot, frame, sizeof(frame), &written)
           == BATTERY_TELEMETRY_INVALID);
    snapshot.battery_pct = 83;

    snapshot.temperature_tenths_c = -401;
    assert(battery_telemetry_format(9, &snapshot, frame, sizeof(frame), &written)
           == BATTERY_TELEMETRY_INVALID);
    snapshot.temperature_tenths_c = 1001;
    assert(battery_telemetry_format(9, &snapshot, frame, sizeof(frame), &written)
           == BATTERY_TELEMETRY_INVALID);
    snapshot.temperature_tenths_c = 240;

    snapshot.battery_health_available = true;
    snapshot.battery_health_pct = 101;
    assert(battery_telemetry_format(9, &snapshot, frame, sizeof(frame), &written)
           == BATTERY_TELEMETRY_INVALID);

    snapshot = fixture();
    assert(battery_telemetry_format(9, &snapshot, frame, 0, &written)
           == BATTERY_TELEMETRY_INVALID);
    assert(battery_telemetry_format(9, &snapshot, NULL, sizeof(frame), &written)
           == BATTERY_TELEMETRY_INVALID);
    assert(battery_telemetry_format(9, &snapshot, frame, sizeof(frame), NULL)
           == BATTERY_TELEMETRY_INVALID);
    puts("PASS BatteryTelemetryCTest (portable C, synthetic values only)");
    return 0;
}
