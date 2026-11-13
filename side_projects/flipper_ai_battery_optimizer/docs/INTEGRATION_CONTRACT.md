# Future integration contract — review required

**Not implemented in Momentum or Android; this is a design contract, not an active BLE endpoint.**

## Existing main-project interfaces checked (2026-11-13)
- Private Flipper `feature/momentum-ble-hardware-status-v62`: `flipper_app/satellite_protocol/ai_app_transport.c`, `ai_ble_bridge.c`, `ai_wire.h`. AI1 frames are limited to **180 bytes**. Bridge requires trusted encrypted/authenticated link, notifications and a viable ATT payload.
- Public Android `feature/android-radio-listening-v238`: `SatelliteProtocol.java`, `FrameCodec.java`, `SatelliteRequestHandler.java`. Current supported inbound types are `HELLO`, `PING`, `ASK`, not a battery snapshot command.
- Existing private Flipper `flipper_app/flipper_ai.c` reads battery percentage/health/charging **locally**. These APIs do not prove phone-readable battery telemetry.

## Proposed (future only)
A versioned read-only power capability negotiated after a trusted HELLO, **not enabled by default**. Add a new allowlisted request/response type only when both clients support it. Keep AI1's 180-byte limit, no unescaped separators/newlines, strict request ID checks, timeout/size handling, and connection-epoch cancellation.

Proposed snapshot fields: monotonic sample time, battery %, optional battery-health %, optional temperature, charging flag, and active-operation flag. Mark absent fields as unavailable; never infer physical current, voltage, or temperature from battery percentage alone. No private device IDs, radio content or location.

Phone adapter -> `BatteryOptimizer.Sample` -> deterministic `evaluate` -> UI advice. Optional offline AI may explain an `Advice` result but cannot bypass safety rules or issue hardware commands. Cloud submission requires separate explicit user opt-in; default stays local.

`suggestedDisplayTimeoutSeconds` / `suggestedTelemetryIntervalSeconds` are **recommendations**, not claims these settings are remotely supported. Read-only status comes first. Any later device adjustment must be allowlisted, user-approved, reversible, and blocked during active NFC/RFID/Sub-GHz/IR/GPIO/Wi-Fi tasks or unstable BLE sessions.

## Validation before later integration
1. Existing public AI1 tests still pass; new extension contract gets separate boundary tests.
2. Android JVM or host tests and private Flipper protocol tests pass without exposing private code in public CI.
3. Physical Flipper + Android BLE trust, disconnect/reconnect, sampling overhead and existing app behavior tested.
4. Battery benefit measured in reproducible conditions; no unsubstantiated savings percentages.
5. No commits or merges to either main-project repository until explicit approval.
