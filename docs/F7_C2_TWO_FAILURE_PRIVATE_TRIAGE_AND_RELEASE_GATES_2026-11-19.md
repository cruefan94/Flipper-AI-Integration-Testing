# F7 C2 exact-head failure: reproducible private triage and release hold

Date: 2026-11-19 12:56 America/Toronto. Public-safe procedural document only; no firmware content, binary, private logs, device identifiers, credentials or signing fingerprints.

## Exact evidence and failure classification
- Private Momentum PR: https://github.com/cruefan94/Flipper-AI-Momentum-/pull/71
- Exact head reported by workstream: `238a54bfc0b1708a827d489cee5d43197871bfb3`.
- Completed failing workflow runs: https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44568518970 and https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44568544991.
- Both `f7-c2-audit` jobs concluded failure (job IDs `135716829135` and `135716925704`). Job metadata alone does **not** establish whether the failure is source, configuration, or infrastructure. A job was provisioned; therefore do not call this a pre-provisioning failure or infer billing.
- An attempted private job-log read returned a BlobNotFound/404 response. No failing step or root cause was confirmed. Keep the private diagnostic in the private repository.
- The two-completed-failure rule is triggered. Approved public-safe fallback is required; **no new fallback dispatch or run ID is verified for this pair**. Do not count the older successful run https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44491711278 as this pair's fallback.

## Private-only triage protocol
1. Authorized maintainer opens both runs' job summaries and step logs **inside private Momentum**; record exact workflow, branch, head SHA, attempt number, failing step and whether runner was provisioned in private issue #5.
2. If Actions logs are inaccessible, record `BLOCKED: Actions read/log access` and required permission; never substitute guesses. Check GitHub-hosted runner status separately from Python/test exit status.
3. If a source/test failure, repair only on the firmware owner's branch and run focused offline tests once before any new CI attempt. Never bypass a safety check or hard-code an unverified C2 address.
4. Invoke the existing **approved encrypted-only public-safe fallback route** only with authorized private Actions:read and workflow-dispatch capability. Public output may include sanitized status, run URL, and hash of encrypted archive; must not include private firmware, unencrypted binary, source, credentials, signing data, raw logs, or device diagnostics.
5. Record fallback run ID, pinned private source SHA in private tracker, completed job outcomes, encrypted-only artifact identity and any missing evidence. If permissions block dispatch, explicitly mark fallback BLOCKED and do not claim success.
6. Do not retry known failed DFU CRC 9-99 updater. Native firmware compile alone does not establish flash safety or a valid updater.

## Candidate promotion gates (all independent)
- **F7**: authoritative C2 flash/radio boundary from verified source; actual linker/section and image placement evidence; native `firmware.dfu` suffix CRC computed from **real** artifact; internal updater file SHA-256 and archive integrity; verified encrypted-only provenance; qFlipper recovery and Momentum compatibility; owner-approved physical flash only afterward.
- **Android**: exact tested commit and CI, package ID, installed-vs-candidate signing certificate continuity and monotonic versionCode. On mismatch, preserve installed app and data; optional separate test package only with explicit owner approval.
- **AI1 BLE**: compare UUIDs, characteristic properties, framing, protocol version, authenticated access, HELLO/ASK/ANSWER behavior, reconnect cancellation and negative tests across pinned firmware/Android commits. Stock Momentum RPC is not proof of AI1.
- **Pi/ESP32**: independently tested commits, electrical safety, transport contracts and owner-led hardware acceptance; no automatic inclusion in firmware/APK.
- **Release ledger**: integration-testing workstream is sole writer of combined candidate ledger. All other branches hand off immutable refs, passing run IDs, hashes and blockers; no simultaneous edits to shared candidate branch.

## Prior baseline
- Phase 1 private release blocker matrix: https://github.com/cruefan94/Flipper-AI-Momentum-/pull/23
- Public-safe failover test coverage: https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/23
- Historical native encrypted F7 job (older revision, **not current acceptance**): https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328
- Latest Pi exact dashboard suite: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44551764387 (host tests, not hardware)
- Android PR #86 remains source/CI/hardware acceptance pending: https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/86

No production merge, installation, flash, firmware publication, device access, or candidate promotion authorized by this document.
