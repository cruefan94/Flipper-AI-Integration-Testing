#include "../firmware/src/protocol.h"
#include <cassert>
#include <cstring>
#include <iostream>

using fz1::Command;
int main() {
    assert(fz1::parse("FZ1|PING") == Command::Ping);
    assert(fz1::parse("FZ1|INFO") == Command::Info);
    assert(fz1::parse("FZ1|CAPS") == Command::Caps);
    assert(fz1::parse("FZ1|STATUS") == Command::Status);
    assert(fz1::parse("FZ1|WIFI_SCAN") == Command::WifiScan);
    assert(fz1::parse("FZ1|LED|ON") == Command::LedOn);
    assert(fz1::parse("FZ1|LED|OFF") == Command::LedOff);
    assert(fz1::parse("FZ1|SENSORS") == Command::Sensors);
    assert(fz1::parse("FZ1|SENSOR|ADC34") == Command::SensorAdc34);
    assert(fz1::parse("FZ1|SENSOR|GPIO27") == Command::SensorGpio27);
    assert(fz1::parse("FZ1|SENSOR|I2C_SCAN") == Command::SensorI2CScan);
    assert(fz1::parse("FZ1|SENSOR|BME280") == Command::SensorBme280);
    assert(fz1::parse("FZ1|SENSOR|DHT22") == Command::SensorDht22);
    assert(fz1::parse("FZ1|SENSOR|GPIO21|WRITE") == Command::Invalid);
    assert(fz1::parse("FZ1|SENSOR|ADC35") == Command::Invalid);
    assert(fz1::parse("FZ1|SENSOR|HC_SR04") == Command::Invalid);
    assert(fz1::parse(nullptr) == Command::Invalid);
    assert(fz1::parse("") == Command::Invalid);
    assert(fz1::parse("PING") == Command::Invalid);
    assert(fz1::parse("FZ1|LED|ON|MORE") == Command::Invalid);
    assert(fz1::parse("FZ1|LED|FLIP") == Command::Invalid);
    assert(fz1::parse("FZ1|WIFI_SCAN|ACTIVE") == Command::Invalid);
    assert(fz1::parse("FZ1|RESET") == Command::Invalid);
    assert(fz1::parse("FZ1|WIFI_JOIN|pass") == Command::Invalid);
    char longline[120]; memset(longline, 'A', sizeof(longline)-1); longline[sizeof(longline)-1] = 0;
    assert(fz1::parse(longline) == Command::Invalid);
    std::cout << "FZ1 parser: tests passed\n";
}
