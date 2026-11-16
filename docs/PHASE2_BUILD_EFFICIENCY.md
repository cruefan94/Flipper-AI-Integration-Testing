# Phase 2: fast CI and build evidence (development PR)

Coordination: https://github.com/cruefan94/Flipper-AI-Integration-Testing/issues/48

This phase preserves the private Momentum source boundary and installs/flashes nothing.

## Host-only artifact provenance

\`scripts/phase2_build_manifest.py\` writes a JSON SHA256 manifest containing a
full Git commit SHA, selected repository, build kind, file size and per-file
digest. It rejects unsafe names, symlinks, duplicate files, unrecognized
repositories, and invalid or tampered manifests.

Example for a locally produced *synthetic* APK fixture:

\`\`\`bash
python3 scripts/phase2_build_manifest.py write \
  --root /tmp/phase2-fixture --output /tmp/phase2-fixture/evidence.json \
  --repository cruefan94/Flipper-AI-Android-Satellite \
  --source-sha aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa \
  --kind integration-fixture artifacts/app.apk
python3 scripts/phase2_build_manifest.py verify \
  --root /tmp/phase2-fixture \
  --manifest /tmp/phase2-fixture/evidence.json \
  --expected-sha aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
\`\`\`

For *real* builds, always supply their actual full source SHA and paths.
Store the manifest alongside build artifacts in **their originating private
or public repository**; do not upload private firmware to this public repo.

The generated evidence records **build artifacts only**. It is never
evidence of valid Android signing, BLE pairing, physical firmware flashing,
working inference or on-device performance. Apply the existing package
signature and first-flash safety checks separately.

Fast public smoke CI runs these tests without downloading source or starting a
full firmware/Android build. Cross-repository candidate matching, build
optimization and release workflows should be reviewed in their respective
repositories before any switch-over.
