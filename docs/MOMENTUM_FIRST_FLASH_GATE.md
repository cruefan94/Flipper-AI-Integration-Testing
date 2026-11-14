# Flipper AI Momentum — first hardware flash gate

Status: **COMPILED / ENCRYPTED ARTIFACT AVAILABLE / NOT HARDWARE VERIFIED**

## Build evidence
- GitHub Actions: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43544527859
- Artifact: `encrypted-flipper-ai-flash-candidate-UNTESTED` (ID `14092829927`)
- Public workflow revision: `3f890345589036aa639a8caa3d7144362d594bb8`
- Upstream Momentum pin: `d3f89dfe2ef6b01839201598e9be1590cba80322`
- Package expiration: 2026-11-21 UTC. Artifact is encrypted; do not publish its passphrase.
- CI verifies updater inventory and SHA256 manifest, encrypts with OpenSSL AES-256-CBC/PBKDF2 (250000 iterations), decrypts in CI, and rechecks archive hashes. No device flash has been tested.

## Mandatory preflight
1. Confirm you can recover the Flipper Zero using the official Flipper recovery process and a working USB data connection to a computer. **Do not start flashing if no recovery path exists.**
2. Save your SD card content, existing settings and current firmware version. Keep an independent known-good official/Momentum updater.
3. Download the artifact ZIP from the linked Actions run. Extract its `.enc` file on a trusted computer. Never send the passphrase in chat, issue comments, screenshots or logs.
4. Locally decrypt (on a computer with OpenSSL installed):
   ```sh
   openssl enc -d -aes-256-cbc -pbkdf2 -iter 250000 -salt \
     -in flipper-ai-updater.tar.gz.enc \
     -out flipper-ai-updater.tar.gz
   ```
   OpenSSL will prompt for the secret passphrase. Do not paste the passphrase into a shell command.
5. Inspect the archive without extracting: `tar -tzf flipper-ai-updater.tar.gz`. It must contain `SHA256-manifest.json` and one `f7-update-*` directory. Reject unexpected absolute paths or `..` components.
6. Extract only after inspecting: `mkdir -p flipper-ai-candidate && tar -xzf flipper-ai-updater.tar.gz -C flipper-ai-candidate`. Confirm the updater files and compare hashes with the manifest. Do not install the outer `.zip`, `.enc`, or `.tar.gz` directly.
7. Use an official supported Flipper firmware update/recovery method appropriate for the extracted updater package; if it cannot recognize the package, **stop** rather than renaming or forcing it.
8. After a successful flash, verify boot, existing applications and settings, and AI BLE behavior with Android Satellite. Record hardware results separately; do not infer hardware success from CI.

## Stop conditions
- Missing passphrase, missing updater files, manifest/hash mismatch, unrecognized updater format, low battery, unavailable recovery method, unexpected device behavior.
- Do not merge the candidate into production or claim flash readiness until real-device verification passes.

## Hardware test checklist
- [ ] SD backup and working recovery method confirmed
- [ ] Archive decrypted and SHA256 manifest checked
- [ ] Firmware update applied with supported tool
- [ ] Device boots and existing Momentum functions remain available
- [ ] BLE advertisement/pairing and AI1 requests work
- [ ] Android Satellite receives a real Flipper response
- [ ] Reboot/reconnect regression passes
