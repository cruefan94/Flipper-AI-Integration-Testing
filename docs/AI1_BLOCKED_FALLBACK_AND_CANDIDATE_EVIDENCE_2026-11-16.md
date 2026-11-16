# AI1 candidate evidence and blocked fallback — 2026-11-16 15:04 ET

Scope: public-safe coordination evidence only. No firmware source, binary, private logs, device identifiers, credentials, APK or encrypted artifact bytes.

## Exact currently surfaced refs (not an approved candidate)
- Firmware queue host-test PR: https://github.com/cruefan94/Flipper-AI-Momentum-/pull/29 ; head `e15d43616337c4fd9c6365fa48883a4ae5c1932d` (per PR description). Depends on PR #28 `109c15c1aa413228ed27fec1eeef272d8d917e06`.
- Android Worker endpoint policy PR: https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/46 ; dependent on Android PR #45 `f404c00862ee014c0c00f8db4c2769c5a91d0b98`. Exact PR #46 head and exact-head CI must be checked.
- Public AI1 metadata parity PR: https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/39 ; source commit `17d1b7fac818ce9eb54955bfb8b0a83937d21699`. Associated PR-triggered smoke run https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43935190950 succeeded, but this alone does NOT establish the parity test itself ran.
- Native encrypted F7 workflow https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328 has a successful custom-firmware job; this does NOT establish actual embedded DFU suffix CRC or flash safety.

## Required two-failure escalation — blocked
Firmware predecessor workflow/branch: two failing private runs `43869652442` and `43869692572`, as documented in private PR #29. These qualify for the two-failure policy **only when confirmed as same workflow and branch**. Inspect exact run identity, failure type (source/test vs runner/permissions), and timestamps in private Actions. Private Actions:read HTTP 403 means automatic failure classification and authorized private-safe dispatch are **BLOCKED**, not successful. Do not assume billing; do not rerun indefinitely or publish any private payload. Approved safe fallback route is draft https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/23 ; require access and verified dispatch ID before claiming it executed.

## Promotion evidence needed
1. Record exact firmware and Android heads, full CI run URLs, and source-specific test results; match AI1 UUIDs, framing, maximum lengths, auth/session generations, disconnect reset, queue behavior, version and contract hash using public-safe vectors.
2. For F7: private-side verify actual `firmware.dfu` suffix CRC and native updater archive SHA-256, source SHA and encrypted-only delivery identity; never retry CRC 9-99 failed updater.
3. For Android: compare installed certificate digest against candidate and verify applicationId/versionCode; signing mismatch prohibits replacement. Side-by-side test requires explicit owner approval.
4. Keep Pi/ESP32/radio optional until independently accepted. No protected merge, flashing, installation or production deployment.

This file is a non-production handoff, not evidence of hardware compatibility or a release authorization.
