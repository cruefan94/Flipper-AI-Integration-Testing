#ifndef FLIPPER_BATTERY_REQUEST_H
#define FLIPPER_BATTERY_REQUEST_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Proposed BAT_GET v1 wire request, not installed in Momentum firmware.
 * Authentication, subscription and negotiated capability must be obtained
 * from trusted BLE service state; this parser never registers a BLE handler.
 */
typedef enum {
    BATTERY_REQUEST_OK = 0,
    BATTERY_REQUEST_INVALID,
    BATTERY_REQUEST_UNAUTHORIZED
} BatteryRequestResult;

BatteryRequestResult battery_request_parse(
    const uint8_t* data,
    size_t length,
    bool authenticated,
    bool subscribed,
    bool capability_agreed,
    uint32_t* request_id
);
#endif
