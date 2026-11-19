# Cross-project release evidence divergence — 2026-11-18

Scope: public-safe release process guidance. No private firmware source, binaries, private logs, credentials, hardware identifiers, or personal diagnostics.

## Why this gate exists

A successful GitHub Actions workflow conclusion is **not** proof that all required jobs executed. A passing host test is not a native F7 build; a successful Android APK build on one branch is not proof that a newer branch's APK builds. Distinct PR branches and commits must not be silently combined into a single release candidate.

## Release candidate evidence (required, fail closed)

For **each** candidate, record repository, exact 40-character commit SHA, branch, workflow name, run URL/ID, job name, job conclusion, artifact name, SHA-256, and provenance. Verify that every mandatory job is `completed/success` (not `skipped`, `neutral`, `queued`, `cancelled`, or absent).

**F7 firmware**: native compilation and updater packaging must actually execute on the pinned firmware SHA. Privately validate F7 hardware target, C2 memory boundaries, real `firmware.dfu` suffix CRC from the generated binary (not synthetic fixture), updater manifest consistency, archive checksums, and encrypted-only artifact routing. Never retry the historical DFU 9-99 failed updater. Keep qFlipper recovery instructions and an owner's explicit hardware-flash approval as separate gates.

**Android**: require an exact-head APK build, package/application ID, versionCode progression, candidate signing certificate digest compared with the installed app, artifact SHA-256, and non-destructive upgrade path. A debug APK signed differently from the installed application must not replace it; any separate test app is opt-in and owner-approved.

**BLE AI1**: pin both firmware and Android SHAs, document AI1 API/spec version and UUID/characteristic properties, authentication and CCCD lifecycle, reconnect/session epoch, status-prefix isolation from stock Momentum RPC, TX/RX framing, and negative tests. Host tests on separate commits do not prove paired device operation.

**Pi, ESP32, Arduino, radio, voice, Termux**: optional independent components until interface contract, safety, build provenance and owner-approved device acceptance are demonstrated.

## CI failure routing (same workflow AND branch)

- Count only completed failing attempts for the same repository, workflow and branch, ordered by completion time. A completed success resets the consecutive failure count. Never count queued/cancelled attempts as completed failures.
- After two consecutive completed failures, or repeated failure before a runner job is provisioned, route to the approved public-safe integration-testing fallback. Record source run IDs, classification (code / runner / permission / unknown), fallback run ID, result and corrective action in the **private** canonical tracker.
- If private Actions:read is unavailable or returns 403, mark fallback **BLOCKED — permission**. Do not call an overall green monitoring workflow proof of private firmware fallback; inspect its actual fallback job and evidence.
- Never publish private firmware source, binary, build logs, keys, tokens, or personal device diagnostics to public Actions/artifacts. Do not weaken release gates or rerun indefinitely.

## Handoff checklist

The integration-testing owner alone updates the combined release ledger. Feature owners submit exact commit, passing run/job, artifact digest and dependencies. Promote only into a controlled non-production candidate after evidence checks. Keep Android APK and native F7 TGZ release status separately at HOLD until all applicable gates pass. Do not merge protected branches, flash hardware, install APKs, or deploy production services without explicit approval.

## Current next verification

Recheck the latest Android branch's failing APK job, distinguish host regression from dependency or compilation failure using authorized job evidence, and obtain a corrected exact-head passing build from its owning workstream. Separately obtain a non-skipped F7 native compilation and CRC/hash evidence; do not infer success from quick source checks.
