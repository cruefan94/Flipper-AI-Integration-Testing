#include "battery_request.h"
#include <limits.h>
#include <string.h>

BatteryRequestResult battery_request_parse(
    const uint8_t* data, size_t length,
    bool authenticated, bool subscribed, bool capability_agreed,
    uint32_t* request_id
) {
    if(request_id) *request_id = 0;
    if(!authenticated || !subscribed || !capability_agreed)
        return BATTERY_REQUEST_UNAUTHORIZED;
    if(!data || !request_id || length == 0u || length > 180u)
        return BATTERY_REQUEST_INVALID;

    static const char prefix[] = "AI1|BAT_GET|";
    static const char suffix[] = "|v1\n";
    const size_t prefix_len = sizeof(prefix) - 1u;
    const size_t suffix_len = sizeof(suffix) - 1u;
    if(length <= prefix_len + suffix_len ||
       memcmp(data, prefix, prefix_len) != 0 ||
       memcmp(data + length - suffix_len, suffix, suffix_len) != 0)
        return BATTERY_REQUEST_INVALID;

    const size_t start = prefix_len;
    const size_t stop = length - suffix_len;
    if(stop <= start || stop - start > 10u) return BATTERY_REQUEST_INVALID;
    if(stop - start > 1u && data[start] == '0')
        return BATTERY_REQUEST_INVALID;

    uint32_t value = 0u;
    for(size_t i = start; i < stop; ++i) {
        uint8_t c = data[i];
        if(c < '0' || c > '9') return BATTERY_REQUEST_INVALID;
        uint32_t digit = (uint32_t)(c - '0');
        if(value > (UINT32_MAX - digit) / 10u)
            return BATTERY_REQUEST_INVALID;
        value = value * 10u + digit;
    }
    if(value == 0u) return BATTERY_REQUEST_INVALID;
    *request_id = value;
    return BATTERY_REQUEST_OK;
}
