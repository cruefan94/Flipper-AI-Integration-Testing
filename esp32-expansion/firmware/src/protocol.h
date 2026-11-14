#pragma once

#include <stddef.h>
#include <stdint.h>

namespace fz1 {
constexpr size_t kMaxLine = 95;
enum class Command : uint8_t {
    Invalid, Ping, Info, Caps, Status, WifiScan, LedOn, LedOff
};
// No allocation; rejects malformed, overlong, unknown or argument-injected lines.
Command parse(const char* line);
}
