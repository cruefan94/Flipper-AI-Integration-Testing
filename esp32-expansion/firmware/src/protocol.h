#pragma once

#include <stddef.h>
#include <stdint.h>

namespace fz1 {
constexpr size_t kMaxLine = 95;
enum class Command : uint8_t {
    Invalid, Ping, Info, Caps, Status, WifiScan, LedOn, LedOff,
    Sensors, SensorAdc34, SensorGpio27, SensorI2CScan, SensorBme280, SensorDht22
};
// No allocation; rejects malformed, overlong, unknown or argument-injected lines.
Command parse(const char* line);
}
