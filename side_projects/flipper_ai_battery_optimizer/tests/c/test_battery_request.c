#include "../../firmware_adapter/battery_request.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static BatteryRequestResult parse(const char* frame, bool auth, bool subscribed,
                                  bool capability, uint32_t* id) {
    return battery_request_parse((const uint8_t*)frame, strlen(frame),
        auth, subscribed, capability, id);
}
static void reject(const char* frame) {
    uint32_t id = 42;
    assert(parse(frame, true, true, true, &id) == BATTERY_REQUEST_INVALID);
    assert(id == 0);
}
int main(void) {
    uint32_t id = 0u;
    assert(parse("AI1|BAT_GET|7|v1\n", true, true, true, &id) == BATTERY_REQUEST_OK);
    assert(id == 7u);
    assert(parse("AI1|BAT_GET|4294967295|v1\n", true, true, true, &id) ==
           BATTERY_REQUEST_OK && id == UINT32_MAX);
    assert(parse("AI1|BAT_GET|8|v1\n", false, true, true, &id) ==
           BATTERY_REQUEST_UNAUTHORIZED && id == 0u);
    assert(parse("AI1|BAT_GET|8|v1\n", true, false, true, &id) ==
           BATTERY_REQUEST_UNAUTHORIZED && id == 0u);
    assert(parse("AI1|BAT_GET|8|v1\n", true, true, false, &id) ==
           BATTERY_REQUEST_UNAUTHORIZED && id == 0u);
    reject("AI1|BAT_GET|0|v1\n");
    reject("AI1|BAT_GET|01|v1\n");
    reject("AI1|BAT_GET|4294967296|v1\n");
    reject("AI1|BAT_GET|7|v2\n");
    reject("AI1|BAT_TELEM|7|v1\n");
    reject("AI1|BAT_GET|7|v1");
    reject("AI1|BAT_GET|7|v1\nBAD");
    reject("AI1|BAT_GET|7|v1\n\n");
    reject("AI1|BAT_GET|a|v1\n");
    reject("AI1|BAT_GET|7|v1|extra\n");
    assert(battery_request_parse(NULL,0,true,true,true,&id) == BATTERY_REQUEST_INVALID);
    assert(battery_request_parse((const uint8_t*)"AI1|BAT_GET|7|v1\n",17,
        true,true,true,NULL) == BATTERY_REQUEST_INVALID);
    puts("PASS BatteryRequestCTest (canonical requests and trust checks, host-only)");
    return 0;
}
