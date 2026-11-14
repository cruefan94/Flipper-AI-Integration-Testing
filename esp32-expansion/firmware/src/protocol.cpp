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
    if(strcmp(cmd, "SENSORS") == 0) return Command::Sensors;
    if(strcmp(cmd, "SENSOR|ADC34") == 0) return Command::SensorAdc34;
    if(strcmp(cmd, "SENSOR|GPIO27") == 0) return Command::SensorGpio27;
    if(strcmp(cmd, "SENSOR|I2C_SCAN") == 0) return Command::SensorI2CScan;
    if(strcmp(cmd, "SENSOR|BME280") == 0) return Command::SensorBme280;
    if(strcmp(cmd, "SENSOR|DHT22") == 0) return Command::SensorDht22;
    return Command::Invalid;
}
}
