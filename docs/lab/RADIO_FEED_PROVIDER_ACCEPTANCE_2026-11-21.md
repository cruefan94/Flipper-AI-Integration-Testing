# Receive-only public feed acceptance gate — 2026-11-21

Parent prototype: PR #327, commit e68d602f46296bb06a14cb16d319e812ee512c41.
Exact parent GitHub Actions: radio metadata tests run 44966321660 SUCCESS; public smoke run 44966321636 SUCCESS. This document is a NEW commit and needs its own exact-head CI.

## Before listing any live source
- Record the named provider, official terms URL, date reviewed, geographic jurisdiction, stream URL provenance, and permission for third-party playback or redistribution. Never include credentials or access tokens.
- Confirm source is intentionally public and unencrypted, lawful to receive in the user's location, and explicitly permitted by the provider. A public URL alone is insufficient.
- Reject restricted emergency-service feeds, encryption circumvention, credential-only services, covert interception, rebroadcast and recording absent independent permission. No transmission functionality.
- Obtain owner approval for each source and confirm current terms immediately before use. Catalog metadata validation does not prove legal permission.
- Use HTTPS with no redirects to private/local networks, avoid embedded secrets, enforce reasonable request timeouts, and do not automatically connect or stream during tests.
- Label CB and fire/police online streams as optional, availability and legality unverified. Do not assume a phone can directly tune AM/FM/CB or police frequencies without a supported receiver.
- USB SDR remains an optional receive-only Pi/Android extension subject to actual tuner compatibility, antenna, local law, and hardware acceptance.

## Release gates
1. Exact-head public-safe offline CI passes with recorded run ID and commit SHA.
2. Provider permissions and Ontario/Canada jurisdiction review are recorded without private data.
3. Owner-operated receive-only playback on Pi/Android verified; no transmit paths.
4. Cross-component API/AI1 compatibility tested, and integration-testing release ledger owner accepts provenance.
5. No APK/F7 promotion without independent artifact/signature/CRC gates; CRC 9-99 F7 updater quarantined, Android existing install protected.
6. Preserve two-consecutive-failure fallback; private Actions:read HTTP 403 means automatic private coverage BLOCKED until configured and verified.

This document does not fetch, play, record or distribute any stream, and changes no hardware or production branch.
