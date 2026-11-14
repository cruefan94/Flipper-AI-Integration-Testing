# Native Flipper Zero Momentum + AI phone update (.tgz)

**Status: EXPERIMENTAL / NOT HARDWARE VERIFIED.** A passing GitHub Actions build proves compilation and archive integrity, not a successful Flipper flash, Bluetooth handshake or AI response.

## Why the new packaging exists

The pinned upstream Momentum build produces both an updater directory named `f7-update-*` and its **native** phone/qFlipper update archive named `flipper-z-f7-update-*.tgz`. Our prior private-source build produced valid compiled updater files but delivered the directory inside an encrypted archive, which was not directly selectable in the Flipper app.

[Integration PR #3](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/3) preserves the upstream-native `.tgz` without modifying or recompressing its internals. CI checks the `update.fuf` F7 target, required `firmware.dfu` and `updater.bin`, the exact native archive member inventory, hashes, and encryption roundtrip. It uploads only encrypted output; private source and decrypted firmware are not made public.

## Firmware package delivery

- CI build: [native mobile updater candidate](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43557522340)
- Artifact after successful build: `encrypted-flipper-ai-mobile-native-tgz-UNTESTED`
- Artifact ZIP contains **`flipper-ai-native-tgz-delivery.tar.gz.enc`**, NOT a Flipper firmware file.
- The passphrase is the user's `FLIPPER_ARTIFACT_PASSPHRASE` GitHub Actions secret. GitHub does not disclose a secret after saving it. If the owner does not know the passphrase, set a **new** secret in the repo and rerun the workflow; do not attempt blind guessing or post secrets in issues/chats.
- The owner can decrypt locally on a trusted Raspberry Pi 4B using OpenSSL. The process does not require flashing via Raspberry Pi; the *extracted native .tgz* can be transferred to the Android phone afterward.

From the directory containing the encrypted file:

```sh
openssl enc -d -aes-256-cbc -pbkdf2 -iter 250000 -salt \
  -in flipper-ai-native-tgz-delivery.tar.gz.enc \
  -out flipper-ai-native-tgz-delivery.tar.gz
# OpenSSL asks for the passphrase interactively; do not put it in command history.
python3 -m tarfile -l flipper-ai-native-tgz-delivery.tar.gz
# Using the public-safe source at scripts/prepare_momentum_flash_package.py:
python3 scripts/prepare_momentum_flash_package.py verify \
  --archive flipper-ai-native-tgz-delivery.tar.gz
tar -xzf flipper-ai-native-tgz-delivery.tar.gz
```

The extracted `flipper-z-f7-update-*.tgz` is the **only** file intended for a normal Flipper firmware updater. Do **not** rename `.enc`, the GitHub artifact ZIP, or the outer delivery `.tar.gz` to `.tgz`.

## Required first hardware verification gate

1. Keep a backup of the Flipper SD card and the [official Momentum mntm-012 recovery updater](https://github.com/Next-Flip/Momentum-Firmware/releases/tag/mntm-012).
2. Confirm the Raspberry Pi with qFlipper has a *working USB data connection* and supported DFU recovery before experimenting. Owning qFlipper is not proof that recovery works.
3. Check updater target/name/checksums and ensure the Flipper Zero battery is charged.
4. Install the native `.tgz` only through a compatible update path; stop if the mobile app does not recognize it.
5. Verify firmware boot, original Momentum apps/functions, Bluetooth pairing/authenticated AI1 link, Android AI Satellite response, reconnect/reboot and recovery path. Record results before any production label.

## Boundaries

No custom firmware has been independently flashed or hardware-tested by this CI. This work does not ship Android AI model weights, enable automatic hardware transmissions, or integrate the battery/Civic side projects. Compiled F7 updater does not include ESP32-S2 firmware. No plaintext private build output should be committed or uploaded to the public repository.
