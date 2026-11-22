# MAIN integration gate triage — 2026-11-22

Public-safe process document. No private firmware source, logs, binaries, credentials, device identifiers or private diagnostics may be copied into this repository.

## Exact-head evidence
- Android PR #132: `e054c9f4cc7689da87a92e2f32edeb18015fedaa`; combined APK workflow 45068584230 **success**; metadata 45068584221 **success**. These results do not verify stable signing, installed-app upgrade, BLE AI1 physical link or release admission.
- Momentum PR #88: `cf738f959de58a162a83db873bcbf66c0eac72ba`; FAP 45067246324 **failure**; F7 45067246380 **failure**; native protocol 45067246313 **failure**; bridge 45067246394 **failure**; C/Java interop 45067246351 **failure**. Different workflows are not two consecutive attempts of the *same* workflow and branch.
- Integration PR #382: `436811ba4539c15de04c1671e31ad75e113fc3ab`; public smoke 45069511707 **success**. PR #384: `1d37ec4250195333929fdb1e86f0b31dac217a5a`; smoke 45072089606 **success**. Smoke results are not native F7/FAP release proof.
- Historical encrypted native firmware fallback 45039819048 passed its firmware job; standalone FAP and exact-artifact DFU suffix CRC remain separate gates.

## Deterministic triage sequence
1. Record repo, workflow name, branch, exact head SHA, run ID, attempt number, job provisioning state, and failed step **privately** when sourced from a private repository.
2. Classify **pre-job/runner** when no runner job was provisioned; **source/test** only when a provisioned job reaches a failing compiler, test, or validation step; **permission** when a 401/403 is observed; **unknown** if evidence is insufficient. Never infer billing from a pre-job failure.
3. Count only consecutive completed failures for the *same workflow and branch*. If count reaches two, or repeated pre-job failure is confirmed, invoke the approved public-safe integration fallback route. A separate protocol fallback is not proof of a FAP build. Record fallback run ID, status, scope and exact pinned source SHA in the **private** tracker.
4. For private Actions 403/missing Actions:read permission, mark fallback **BLOCKED** until an approved least-privilege credential/permission is configured in the private secret store. Never print tokens or private logs in public summaries. Do not loop retries or weaken test gates.
5. Require Android candidate artifact SHA-256, versionCode/package ID and signer certificate fingerprint comparison against the existing installed app **before** considering upgrade. A different signer means **NO REPLACE/UNINSTALL**; opt-in side-by-side test only with owner approval.
6. Require native F7 updater exact source SHA, encrypted-only artifact identity, archive SHA-256, updater manifest/internal hashes, real `firmware.dfu` suffix CRC validation and documented qFlipper recovery. The prior CRC 9-99 updater is permanently quarantined. Synthetic fixtures are insufficient.
7. Require pinned BLE AI1 version and identical request/response/error/timeout semantics across Android, FAP and gateway, passing cross-language contract tests, then owner-approved physical verification. Stock Momentum RPC alone does not establish AI1 link readiness.
8. Only the integration-testing workstream promotes a combined candidate after evidence review. Pi/ESP32/radio/voice remain optional until their own compatibility and safety gates pass.

## Private MAIN handoff template
`repo | branch | SHA | PR | workflow/run/attempt | provisioned? | classification | corrective step | fallback run/scope | APK included? | F7 included? | signer/hash/CRC/AI1 evidence | blocker | next owner`

Public documentation must contain only sanitized workflow metadata and no private-source-derived details.
