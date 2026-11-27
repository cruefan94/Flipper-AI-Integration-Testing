# Northern Circuit hardware bridge v1 — development proposal

**Status:** design and contract-test prototype only; not deployed or physically validated. `Tradesman Pro` remains the top-priority app. This is a separate Flipper/AI Satellite hardware-integration workstream. Keep the Android Satellite app in its existing repository; do not create a replacement Android app.

## Devices and responsibilities

| Device | Responsibility | Initial connection |
| --- | --- | --- |
| Raspberry Pi 4B (4 GB) | Trusted gateway, Python router, AI and approved automation | Ethernet or local Wi-Fi; local USB/UART for development |
| Android AI Satellite (existing single APK) | Phone UI, voice/AI, device chooser, signed-in gateway access and approvals | Existing BLE to Flipper; authenticated HTTPS or VPN to Pi |
| Flipper Zero (official Momentum, BLE name Sarah) | Portable UI for reading status and triggering approved actions | Existing AI1 BLE path via Android, or 3.3 V UART to P4/Pi via custom .fap |
| Waveshare ESP32-P4 + ESP32-C6 (planned, exact SKU/pinout pending) | High-throughput hardware controller; C6 provides Wi-Fi/BLE | Ethernet or UART to Pi; Wi-Fi via ESP-Hosted only after validation |
| Existing ESP32-WROOM-32 | First physical prototype for control and telemetry, **before purchasing P4** | 3.3 V UART to Pi, or LAN Wi-Fi |
| Arduino Uno | 5 V sensor/actuator test node | UART with bidirectional level shifting, or correctly converted I2C |
| Termux on Android | Explicitly approved local Python task runner; optional legacy private-GitHub-issue diagnostics | Android app `RUN_COMMAND` integration only with consent and correct permissions; existing private issue prototype retained independently |

**Physical constraints:** UART TX/RX cross, common signal ground, match baud and framing, never feed Uno 5 V logic into P4/Pi/Flipper 3.3 V pins. Do not tie together separately powered rails. Choose reserved GPIO only after exact P4 board schematic and onboard peripheral allocation are confirmed. Flipper-specific GPIO is **not** a generic BLE or Wi-Fi link.

## Communication path

```text
                         [Android AI Satellite]
                          / BLE          \ authenticated HTTPS/VPN
                   [Flipper Zero]       [Pi 4B Python Gateway]
                      | 3.3 V UART          /  |       \
                      |              local UART LAN   approved Android task request
                [ESP32-P4 + C6] <-----> |   |        [Termux]
                      |                   |  |
             sensors / peripherals  [WROOM-32]---[Uno via level shifter]
```

These are **possible links, not all simultaneous links already working**. Prefer a routed star: all components need not be wired together. Termux is on the Android device, not on the Flipper/P4/Uno. For remote control, the Pi is an authenticated always-on network gateway; no direct public port forwarding to boards or arbitrary command service.

## v1 message contract

This prototype deliberately separates the **application envelope** from the **transport**:
- Envelope: UTF-8 JSON, max 4096 bytes, version `1`, explicit `kind`, `request_id`, `source`, `target`, `action`, and `args`. Request IDs are used to reject duplicates and correlate responses.
- Supported request actions at first: `device.ping`, `device.status`, `device.capabilities`, `telemetry.read`, `script.list`, `script.request`. The **only script-execution request** is a registry ID, never source code, a shell command, or a path.
- Audio contract actions (design prototype): `audio.play`, `audio.stop`, and `audio.status`. Audio requests target `p4` only and do **not** carry audio bytes, filesystem paths or shell commands. These are validated request shapes, not a working speaker driver.
- UART/TCP test adapter: 2-byte big-endian length followed by one JSON envelope. Production TCP should use authenticated TLS or protected VPN; UART framing alone offers **no security**.
- Existing Flipper↔Android AI1 GATT frames use their *existing 180-byte limit and BLE state machine*. Do not transmit a 4096-byte bridge frame as a single AI1 packet. Add an Android translator or explicitly designed chunking/ACK layer with MTU checks when integrating.
- P4/C6 ESP-Hosted is a separate software dependency. Validate Ethernet and UART independently before wireless.
- Each authenticated endpoint needs a device identity, allowed action/target list, nonce or request-ID replay protection, expiration policy, rate limits and audit log. The Python contract module is **not** an authentication implementation.

Example **non-executable** request:

```json
{"version":1,"kind":"request","request_id":"demo-001","source":"android","target":"pi","action":"device.status","args":{}}
```

Approved script **selection** request (NOT permission to execute):

```json
{"version":1,"kind":"request","request_id":"demo-002","source":"android","target":"termux","action":"script.request","args":{"script_id":"device_diagnostics","params":{}}}
```

`script.request` is a proposal that the **receiving** gateway must authorize against a locally configured script registry; Termux must still enforce owner consent and Android's app permissions. Never execute untrusted user-supplied shell text from BLE, HTTP, GitHub issue bodies or AI-generated text.

## Development sequence and acceptance gates

1. **Contract and safety:** implement pure-Python serialization/framing validation and unit tests in this branch; preserve AI1 GATT and existing app binary unchanged.
2. **Pi ↔ WROOM-32 hardware:** UART ping/status and telemetry with serial settings, a read-only command registry and captured test logs.
3. **Android Satellite ↔ Pi:** add a small device-management screen/adapter on a *separate Android branch*, using the v1 envelope over a secure connection. Preserve current working single-APK build, BLE reconnect and offline AI; no radio-mode changes in this integration branch.
4. **Termux:** integrate Android `RUN_COMMAND` through a permission-checked, opt-in adapter and return sanitized results. The existing `termux/termux_bridge.py` polls **private GitHub issues**, and is not the Android adapter; retain it for diagnostics. Never enable its arbitrary `shell` operation without local review.
5. **Flipper:** adapt existing custom app through validated AI1-to-bridge translation and/or a dedicated UART .fap. No automatic firmware flashes; do not assume generic serial-to-BLE bridging.
6. **P4 + C6:** after exact SKU is confirmed and hardware arrives, verify pin mapping, serial, wired Ethernet, ESP-Hosted wireless, and only then cross-device control.
7. **Uno:** level shifter, safe power review, UART test, isolated outputs. No motors, relays or high-power loads without drivers.

**Success criterion:** show an end-to-end owner-authorized `device.status` request from Android or Flipper → Pi → WROOM-32/P4 → response; demonstrate rejected unauthorized requests, duplicate IDs and malformed frames; then demonstrate a *locally approved* Termux diagnostics script. Physical validation, Android integration, Flipper app and P4 hardware remain pending.

**Release guard:** development branch and draft PR only; no automatic merges, APK installs, Flipper flashes, external exposure, or production changes. No credentials, private Momentum source, firmware artifacts or personal data in this public repository.

## Shared audio output — phase 1 (contract added, hardware playback pending)

**Purpose:** treat the speaker attached to the planned Waveshare ESP32-P4 board as a shared output for owner-authorized notifications and sound effects from the Flipper Zero, Raspberry Pi 4B and existing Android AI Satellite. Keep this within the hardware bridge draft; Tradesman Pro and installed firmware/APKs remain unchanged.

**Initial transport and playback design:**
1. Put a small, pre-approved sound collection (e.g. `beep`, `notification_1`, `alert_ok`) on the P4's microSD, using a WAV/PCM format compatible with the codec/driver selected after board validation.
2. The Flipper's eventual custom .fap sends a short `audio.play` request over existing AI1 BLE to Android or validated 3.3 V UART to the gateway. Android translates AI1 messages, preserving its actual 180-byte transport constraint. Android and the Pi can initiate the same bridge envelope over their authenticated link.
3. The Pi or authenticated local router checks **source identity, per-device permissions, request replay/expiry, and rate limits** before forwarding a permitted request to P4. Schema validation alone does not authorize playback.
4. The P4 checks the `sound_id` against a fixed local manifest, checks output volume/power constraints and plays that sound through the board's audio driver. The P4 returns correlated `ok`/`error` response and optional status; no arbitrary paths or uploads are accepted.
5. Optional follow-up: playback queue, volume limits, handling of busy/offline output, and eventually authenticated packetized streaming with explicit buffer/codec negotiation. **Streaming is out of scope for phase 1.**

Example — **non-executing contract** (not a working end-to-end implementation):

```json
{"version":1,"kind":"request","request_id":"audio-001","source":"flipper","target":"p4","action":"audio.play","args":{"sound_id":"notification_1","volume":50}}
```

Other v1 actions: `audio.stop` and `audio.status` must use empty `args`. `audio.play` accepts exactly a lowercase manifest `sound_id` plus optional integer `volume` in **0–100**; the receiver must enforce a lower physical output limit if appropriate. The contract rejects path traversal, file paths, binary/audio transfer and extra arguments. It contains **no executable audio player**, no GPIO commands, no open network listener, and no permission bypass.

**Hardware gate:** verify exact P4 board variant, installed speaker impedance/power rating, codec/amplifier path, microSD wiring, audio sample format and ESP-IDF audio drivers before adding firmware. The board speaker is not a direct wired amplifier for the Flipper's buzzer; Flipper sound-file playback needs a future app adapter and gateway. The first physical demo is Flipper/Android/Pi requests → P4 manifest lookup → audible notification → status response, followed by interrupted playback and unauthorized-request tests.
