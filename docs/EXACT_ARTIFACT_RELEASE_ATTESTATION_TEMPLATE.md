# Exact-artifact release attestation — public-safe template

Status: **template only**. This file contains no private firmware source, binaries, credentials, device identifiers or personal logs. Do not mark a candidate releasable using a green workflow alone.

## Evidence record (one per exact candidate)
- Component and repository (public-safe identifier):
- PR / branch / exact immutable commit SHA:
- Workflow name, completed run ID, attempt, conclusion, and URL:
- Distinguish: source/contract test | host/runner probe | native compile | package inspection | physical acceptance.
- Artifact ID, expiration, and encrypted-only upload status (never link plaintext private firmware):
- Public-safe provenance attestation ID (private source SHA stays in private tracker if sensitive):
- Reviewer and date:
- Admission verdict: HOLD / BLOCKED / ACCEPTED FOR OPT-IN TEST (not production).

## Android upgrade gate
- Compare *installed* and candidate applicationId/packageName, signer certificate SHA-256 and versionCode from authorized local metadata; record comparison verdict without uploading personal/device diagnostics.
- Same-package upgrade requires signer continuity (or a verified supported signing lineage) and a valid non-downgrade versionCode. A different package is a separate opt-in installation, not an upgrade.
- Signing mismatch or missing metadata => HOLD. Do not uninstall/replace the installed app or auto-install.
- Verify APK hash, embedded AI1 protocol/version, BLE message framing, error behavior, reconnect and offline/online fallback on approved devices before declaring integrated.

## Native F7 Momentum updater gate
- Native F7 build from exact approved private commit; verify `firmware.dfu` **actual suffix CRC** from updater contents, not only synthetic fixtures.
- Verify every updater manifest member's SHA-256, archive identity, target compatibility, encrypted-only artifact transport and reproducible package instructions via private authorized route.
- Require original Momentum functionality, qFlipper backup/recovery instructions and owner authorization for any physical flash.
- **NEVER reuse the CRC 9-99 failed updater.** No public private-firmware binaries, source, decrypted logs, keys or hashes that expose confidential identifiers.

## Two-failure fallback decision record
- Key failures by exact repository + branch + workflow, in chronological completed-at order; record run IDs and attempts.
- After **two consecutive completed failures** on the same key, or repeated pre-provisioning failure, invoke only the established approved public-safe private-firmware fallback.
- Record trigger run IDs, failure class (code vs runner vs permissions/unknown), fallback run ID, job outcome, artifact confidentiality and corrective action.
- HTTP 403 or missing private Actions:read => **BLOCKED**; do not claim a fallback ran or assume billing caused failure.
- A passing unrelated branch, synthetic test, or fallback compilation does not clear exact-head release gates.

## Cross-project handoff
Only the integration-testing owner updates the combined candidate ledger. Feature owners submit exact commit, dependencies, passing workflow URL and explicit missing gates. Pi/ESP32/Arduino/radio remain optional components until native compatibility and safety are demonstrated. Report verified evidence to private canonical issue #5 without secrets. No protected merge, deployment, device flash or APK installation in this workflow.
