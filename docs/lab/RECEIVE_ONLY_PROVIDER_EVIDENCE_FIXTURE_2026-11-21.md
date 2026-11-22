# Receive-only feed provider evidence fixture (offline, public-safe)

Status: **UNVERIFIED TEMPLATE — NO REAL FEEDS APPROVED**. This document is an acceptance fixture, not a feed catalog or legal authorization.

## Purpose
Capture evidence for a proposed public audio source without publishing URLs that may contain private tokens or enabling any transmitter. The existing metadata preflight and CI tests validate *declared fields*, not a provider's real permission or Canadian legal compliance.

## Evidence record (one record per feed)

| Field | Required evidence |
|---|---|
| Internal fixture ID | Non-identifying local label, e.g. `example-fm-001` |
| Service | AM/FM broadcast, public CB feed, or public fire/police stream |
| Operator and official source | Provider name and independently verified official documentation |
| Rights | Exact terms permitting personal live listening; note whether caching, recording, transcription and redistribution are prohibited |
| Access | Public, no authentication bypass, no subscriber/private/dispatch-only source |
| Location and law | Jurisdiction, Ontario/Canada legal review and provider restrictions; escalate uncertainty |
| URL safety | HTTPS; reject embedded credentials, localhost, private IPs, redirects to private networks and untrusted playlist targets |
| Capabilities | Phone/Pi internet audio; USB SDR only when hardware/driver/antenna and lawful reception are separately proven |
| Consent | Explicit owner approval for any device/network playback |
| Verification | Reviewer, review date, evidence link, and expiration/recheck date |
| Release gate | `BLOCKED` until all above evidence exists and offline tests pass |

## Synthetic examples — deliberately not playable

1. `example-fm-001`: `https://example.invalid/live`; permission **UNKNOWN**; result **BLOCKED**.
2. `example-public-safety-002`: `https://example.invalid/dispatch`; operator approval **UNKNOWN**; result **BLOCKED**.
3. `example-cb-003`: `http://127.0.0.1/audio`; unsafe network target; result **REJECT**.

`example.invalid` is reserved for documentation. Do not replace with a live URL until reviewed. A metadata preflight pass is **not** evidence of lawful access.

## Acceptance sequence
1. Review provider terms and Canadian/Ontario rules, including restrictions on interception, recording and disclosure. Do not assume every publicly reachable stream is authorized.
2. Run offline feed metadata tests on the exact candidate commit and retain run ID and result.
3. Independently inspect the feed endpoint and redirect/playlist handling without exposing tokens, private addresses or internal logs in public CI.
4. On a separate, explicitly approved owner-operated device, test receive-only playback with no TX capability, recording or redistribution enabled.
5. Hand off exact source commit, test run, provenance, unresolved restrictions and compatibility to the integration-testing release ledger owner. Do not promote to Android APK or F7 firmware until separately accepted.

## Project boundaries
No network calls, feed playback, radio transmission, device control, private firmware, credential handling or production integration is performed by this fixture. The two-consecutive-failure fallback remains in force; private Actions:read HTTP 403 is **BLOCKED**, not a successful failover. Failed F7 CRC 9-99 image must not be retried; existing Android app must not be replaced due to signing mismatch.
