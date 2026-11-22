# Stock Momentum RPC AI1 cross-project acceptance gap — 2026-11-21

PUBLIC-SAFE source/CI handoff only. No private source, binaries, logs, identifiers, or credentials.

## Exact reviewed refs
- Private Momentum draft PR #82: `candidate/stock-momentum-rpc-ai1-fap-20261121`, `de2472686dc0d8b8bbde870e98f76e7c013e807a`.
- Android draft PR #116: `ci/android-isolated-apk-preflight-20261121`, `5d58024d64bcabcd15c365ea2fce70ba45b219b4`.
- Integration draft PR #328: `19c8916b6b6dacc477ba4ee9cd52599e35b48e3a`; public smoke run #44969272474 succeeded.
- Native historical F7 run #43828499328 is **not** an attestation for current PR #82 or current PR #22.

## Critical interface distinction
Stock Momentum BLE RPC and custom AI1 BLE GATT are **different transports**. PR #82's external FAP uses RPC AppStart(args="RPC") plus RPC application-data exchange. Android's existing stock RPC diagnostic ping is **not** AppStart, AppData, or AI-ready. No peer implementation or physical handshake has been proven.

## Exact peer acceptance contract (proposed cross-component test vectors)
1. Phone remotely invokes stock RPC AppStart with `RPC` argument and receives app-start success; manual FAP launch must remain disconnected.
2. Flipper application-data sends exactly `AI1|HELLO|1|flipper-v1\n` (LF only); Android responds `AI1|HELLO_ACK|1|android-v1\n` through the RPC AppData envelope.
3. Only after ACK and live RPC session is AI-ready allowed. Ping, pairing, or connected-GATT alone must not set AI-ready.
4. Flipper sends `AI1|ASK|2|question\n`; Android returns `AI1|ANSWER|2|response\n` or `AI1|ERROR|2|reason\n` with the same request ID.
5. Both peers reject mismatched IDs, wrong message order, duplicate/late replies, missing LF, reserved pipe/control bytes, malformed UTF-8, and frames over **180 UTF-8 bytes**. Confirm maximum includes terminator in both implementations before passing boundary tests.
6. Session-close, AppExit, queue overflow, timeout, and remote app restart must clear readiness, reject stale responses, and require a fresh handshake.
7. No implicit online/cloud fallback or remote hardware action. Verify explicit online consent separately.

## CI and release gates
- Add/execute **Android-side RPC AppStart/AppData tests** on its own feature branch, owned by Android workstream. Do not assume PR #116's APK metadata gate implements this transport.
- Execute Flipper portable host protocol tests and **native standalone FAP-only compile** at exact PR #82 SHA. Private Actions runs #44959750600, #44959750614, #44959750300, #44959750275, #44959750236 failed across distinct workflows; this is not proof of two consecutive failures in one workflow.
- Distinguish zero-step runner provisioning from compiled-code failures using private job annotations. If repeated pre-provisioning failure or two consecutive completed failures on the **same workflow + branch**, dispatch the approved public-safe private-firmware fallback and record both run IDs. Private Actions:read 403 => **BLOCKED**, not a successful fallback.
- Android candidate requires real APK package ID, installed-app signer comparison, increasing versionCode, opt-in side-by-side identity and physical RPC AI1 tests. Never replace/uninstall installed app.
- F7 updater requires exact source SHA, real `firmware.dfu` suffix CRC, internal manifest SHA-256, encrypted-only artifact identity and verified qFlipper recovery. Known CRC 9-99 updater is permanently excluded.
- Pi/ESP32/radio/voice remain optional separate components until exact acceptance evidence exists.

**Promotion decision:** HOLD both unified APK and native F7 updater. No production merge, flash, install, artifact publication, or physical validation asserted.
