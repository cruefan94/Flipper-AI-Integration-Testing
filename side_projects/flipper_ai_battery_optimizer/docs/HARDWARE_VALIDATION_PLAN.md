# Hardware validation plan (future; not yet performed)

**Scope:** This branch contains a phone-compatible pure Java prototype. It cannot presently read live Flipper power data via the existing AI1 protocol, and it never applies device power settings. Do not treat synthetic unit tests as actual battery improvements.

## Prerequisites
- Explicit user approval to add read-only power telemetry to the private Momentum build and Android BLE handler in a **separate integration branch**.
- Stable, trusted BLE connection on both devices; optional BAT_TELEM capability negotiated after HELLO. A standard Momentum pairing is not by itself sufficient.
- A verified firmware power API with permissions and consistent data semantics. If temperature, health, or active task state is unknown, declare it missing rather than inventing values.
- No private firmware sources, tokens, user logs, or hardware identifiers published to the public CI workspace.

## Stage A — protocol and safety
1. Test that remote battery reads require user enablement, trusted link, negotiated capability, foreground UI, and idle hardware.
2. Validate known-good BAT_TELEM, missing/duplicate/extra fields, integer boundaries, size limits and strict request IDs.
3. Interrupt BLE during a read; reconnect under a new epoch and confirm no old response is accepted.
4. Verify recovery backoff and device activity: three-to-five-minute intervals, never an uncontrolled high-frequency poll.
5. Confirm settings are never altered and the app remains usable without the power feature.

## Stage B — physical baseline and candidate comparison
- Record at least **three comparable trials per group** (baseline and candidate), each 30 minutes or longer with at least two battery percentage points of discharge. Longer trials are preferable because reported percentage values are coarse.
- Fix the Momentum version, device, phone, Bluetooth environment, display configuration, ambient conditions, and workload type. Alternate baseline/candidate sessions if possible to avoid drift.
- Keep charging disconnected for the entire test. Discard trials with interruptions or background hardware changes.
- Capture start/end battery percentage, elapsed monotonic time, test profile, workload and any known ambient temperature. Collect optional current/voltage only if the firmware supports them safely.
- Compare median percentage-points/hour, not estimated watt-hours. The helper's output is explicitly provisional and NOT proof of statistically significant battery savings.
- Verify optimization overhead (phone CPU use, Flipper wakeups/notifications, BLE connection stability and temperature) has not worsened.

## Release/integration gates
- Public standalone Java/AI1 contract CI green.
- Private Flipper host/unit tests and Android app CI green without credential leakage.
- Real hardware BLE tests including disconnect, consent, active task and charge cases.
- Repeatable non-regressive results before claiming any benefit.
- Explicit user go-ahead before merging into main firmware or Android app.

## Expected result
A baseline of measured battery usage, verified absence of unsafe changes, and an evidence-backed decision about whether to expose battery recommendations in the Android UI.
