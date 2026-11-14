// Flipper AI ESP32 Expansion, portable reference firmware for classic ESP32 DevKit.
// Compile for the exact target before flashing. No cloud keys or automatic connections.
#include <Arduino.h>
#include <WiFi.h>
#include "protocol.h"

#ifndef FLIPPER_ESP_LED_PIN
#define FLIPPER_ESP_LED_PIN -1
#endif

static char line[fz1::kMaxLine + 1];
static size_t used = 0;
static bool discard_oversized = false;

static void finish_reply() { Serial.println("FZ1|END"); }

static void passive_scan() {
    // Explicitly passive: no probe requests, association, deauth or injection.
    WiFi.setAutoReconnect(false);
    WiFi.mode(WIFI_STA);
    const int16_t count = WiFi.scanNetworks(false, false, true, 120);
    if(count < 0) {
        Serial.println("FZ1|ERR|SCAN_FAILED");
        finish_reply();
        return;
    }
    Serial.printf("FZ1|OK|NETWORKS=%d\n", (int)count);
    const int16_t shown = count < 8 ? count : 8;
    for(int16_t i = 0; i < shown; ++i) {
        String name = WiFi.SSID(i);
        char clean[33];
        size_t n = 0;
        for(size_t j = 0; j < name.length() && n < sizeof(clean) - 1; ++j) {
            unsigned char c = (unsigned char)name[j];
            clean[n++] = (c >= 32 && c <= 126 && c != '|') ? (char)c : '_';
        }
        clean[n] = 0;
        Serial.printf("FZ1|DATA|SSID=%s,RSSI=%d,CH=%d\n", clean,
                      (int)WiFi.RSSI(i), (int)WiFi.channel(i));
    }
    WiFi.scanDelete();
    finish_reply();
}

static void execute(fz1::Command cmd) {
    switch(cmd) {
    case fz1::Command::Ping:
        Serial.println("FZ1|OK|PONG");
        break;
    case fz1::Command::Info: {
        String model = ESP.getChipModel();
        Serial.printf("FZ1|OK|CHIP=%s,REV=%d,CORES=%d\n",
                      model.c_str(), (int)ESP.getChipRevision(), (int)ESP.getChipCores());
        break;
    }
    case fz1::Command::Caps:
#if FLIPPER_ESP_LED_PIN >= 0
        Serial.println("FZ1|OK|CAPS=INFO,STATUS,WIFI_PASSIVE_SCAN,LED");
#else
        Serial.println("FZ1|OK|CAPS=INFO,STATUS,WIFI_PASSIVE_SCAN");
#endif
        break;
    case fz1::Command::Status:
        Serial.printf("FZ1|OK|FREE_HEAP=%lu,UPTIME_MS=%lu\n",
                      (unsigned long)ESP.getFreeHeap(), (unsigned long)millis());
        break;
    case fz1::Command::WifiScan:
        passive_scan();
        return; // passive_scan emitted its own END
    case fz1::Command::LedOn:
    case fz1::Command::LedOff:
#if FLIPPER_ESP_LED_PIN >= 0
        digitalWrite(FLIPPER_ESP_LED_PIN, cmd == fz1::Command::LedOn ? HIGH : LOW);
        Serial.println("FZ1|OK|LED_SET");
#else
        Serial.println("FZ1|ERR|LED_NOT_CONFIGURED");
#endif
        break;
    default:
        Serial.println("FZ1|ERR|INVALID_COMMAND");
    }
    finish_reply();
}

void setup() {
    Serial.begin(115200);
#if FLIPPER_ESP_LED_PIN >= 0
    pinMode(FLIPPER_ESP_LED_PIN, OUTPUT);
    digitalWrite(FLIPPER_ESP_LED_PIN, LOW);
#endif
}

void loop() {
    while(Serial.available() > 0) {
        const int raw = Serial.read();
        if(raw < 0) break;
        const char c = (char)raw;
        if(c == '\n') {
            if(discard_oversized) {
                Serial.println("FZ1|ERR|LINE_TOO_LONG");
                finish_reply();
            } else {
                line[used] = 0;
                execute(fz1::parse(line));
            }
            used = 0;
            discard_oversized = false;
        } else if(c != '\r' && !discard_oversized) {
            if(used < fz1::kMaxLine) line[used++] = c;
            else { used = 0; discard_oversized = true; }
        }
    }
    delay(1);
}
