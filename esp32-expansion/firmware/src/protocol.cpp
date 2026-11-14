#include "protocol.h"
#include <string.h>

namespace fz1 {
Command parse(const char* line) {
    if(!line) return Command::Invalid;
    const size_t n = strnlen(line, kMaxLine + 1);
    if(n < 5 || n > kMaxLine || strncmp(line, "FZ1|", 4) != 0) {
        return Command::Invalid;
    }
    const char* cmd = line + 4;
    if(strcmp(cmd, "PING") == 0) return Command::Ping;
    if(strcmp(cmd, "INFO") == 0) return Command::Info;
    if(strcmp(cmd, "CAPS") == 0) return Command::Caps;
    if(strcmp(cmd, "STATUS") == 0) return Command::Status;
    if(strcmp(cmd, "WIFI_SCAN") == 0) return Command::WifiScan;
    if(strcmp(cmd, "LED|ON") == 0) return Command::LedOn;
    if(strcmp(cmd, "LED|OFF") == 0) return Command::LedOff;
    return Command::Invalid;
}
}
