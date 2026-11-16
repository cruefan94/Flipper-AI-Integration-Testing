# Pi health monitor — isolated source milestone

Run on Raspberry Pi OS from the repository root:

```sh
python3 raspberry_pi/pi_health_monitor.py --once
python3 raspberry_pi/pi_health_monitor.py --interval 10
```

The default interval is 10 seconds; smaller intervals are rejected. Stop with Ctrl+C. This reads only /proc and /sys thermal telemetry. No privileged access, hardware writes, network listener, Flipper flash, ESP32 control, or Pironman fan setting changes. Temperature may be null if the sysfs path is absent. Memory pressure requires /proc/pressure/memory. Values are local only unless the owner explicitly chooses to share them.

Local synthetic tests: `cd raspberry_pi && python3 -m unittest -v test_pi_health_monitor.py`. These are not physical Pi tests.

## Separate Pi support streams

- Pironman desktop UI: prior ZIP milestones exist in conversation, not confirmed imported to GitHub; inspect exact original Pironman config keys before writing settings. Cooling service remains authoritative.
- 10-second Pi/OLED/Flipper/ESP32 monitor: this milestone covers read-only Pi OS CPU temperature, memory, uptime and memory pressure only; OLED, Flipper and ESP32 monitoring still pending and must be opt-in.
- Pi OS performance/browser cleanup: future advisory-only recommendations; never delete browser data or run privileged cleanup automatically.
- qFlipper workstation: existing bridge PR #19 covers read-only USB and updater inventory; no physical backup or recovery verification.
- Pi-local AI: existing optional OpenAI client in PR #19; do not infer an offline runtime is installed.
- Phone-to-Pi remote: private issue bridge exists in PR #19, not an authenticated LAN server; future secure remote access must be opt-in.
- BLE/Wi-Fi/USB gateways: architecture pending; do not expose listeners or assume paired Bluetooth implies an IP link.

## Integration handoff

Optional Pi support component only; no change to Android Satellite APK or native F7 Momentum updater candidate. The integration-testing workstream exclusively owns the combined candidate ledger. Preserve the two-consecutive-failure public-safe CI fallback policy and report private Actions:read HTTP 403 as BLOCKED, not as a successful dispatch. Never retry the known failed DFU CRC 9-99 updater or replace the owner's installed Android app.
