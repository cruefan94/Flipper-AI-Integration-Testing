# Flipper AI Momentum + ESP32: Android/Termux verified extraction

**Compilation: PASSED. Hardware flashing: NOT TESTED OR APPROVED.**
This guide retrieves, decrypts and verifies the combined development package; it does not flash either device.

## Exact source and CI evidence

Private integrated firmware source: 5501cb9b9205a87bec79e7810103a4757a8bb665.
Android BLE candidate: c8ba436e19b7a78f05a3e7b12b77cfc3dc258a91.

- [Full native build passed](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43753113437): compiled Momentum F7 native update, ESP32 Manager, separate GPL flasher app and classic ESP-WROOM-32 reference firmware; encrypted round-trip passed.
- [Android/Termux verifier regression tests passed](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43757312639).
- Combined GitHub Actions artifact: encrypted-FlipperAI-ESP32-COMPLETE-NEXT-FLASH-CANDIDATE-UNTESTED (GitHub artifact ID 14178055876, approximately 12.9 MB).
- Artifact expires **November 22, 2026 around 19:45 UTC**. Keep an encrypted backup before then.

The Actions download is an *outer ZIP* containing one encrypted .zip.enc file. **Do not try to flash either file.**

## On the Android phone with Termux

1. Open the successful GitHub Actions run above, sign in if necessary, and download the combined artifact from **Artifacts** into Android Downloads. Do not extract it on the Flipper SD card.
2. In Termux, install utilities and grant storage permission:

~~~sh
pkg install python openssl-tool unzip curl
termux-setup-storage
mkdir -p "$HOME/flipper-ai-preview"
cd "$HOME/flipper-ai-preview"
ls "$HOME/storage/downloads"
~~~

3. Copy the downloaded GitHub Actions ZIP into the private Termux directory. If Android gave it a different name, use the exact name shown by ls:

~~~sh
cp "$HOME/storage/downloads/encrypted-FlipperAI-ESP32-COMPLETE-NEXT-FLASH-CANDIDATE-UNTESTED.zip" .
unzip "encrypted-FlipperAI-ESP32-COMPLETE-NEXT-FLASH-CANDIDATE-UNTESTED.zip"
~~~

The extracted file should be named FlipperAI_ESP32_Complete_Flash_Candidate_UNTESTED.zip.enc.

4. Decrypt with the SAME private passphrase used for the repository secret FLIPPER_ARTIFACT_PASSPHRASE. GitHub Secrets cannot show its saved value. **Never share the passphrase in a chat, command argument, screenshot or log.** OpenSSL will prompt for it privately.

~~~sh
openssl enc -d -aes-256-cbc -pbkdf2 -iter 250000 -salt \
  -in "FlipperAI_ESP32_Complete_Flash_Candidate_UNTESTED.zip.enc" \
  -out "FlipperAI_ESP32_Complete_Flash_Candidate_UNTESTED.zip"
~~~

If decryption fails, stop. Do not flash any resulting incomplete file. An unavailable passphrase requires securely creating a new encrypted build with a new known passphrase.

5. Download the verified public source of the phone-side bundle validator and run it. It will check all contained files, pinned private revision, the F7 target and the updater manifest, then optionally extract ONLY the genuine Flipper native .tgz:

~~~sh
curl -fL --retry 2 \
  "https://raw.githubusercontent.com/cruefan94/Flipper-AI-Integration-Testing/030c7ae46c28eb09b9433a9df629acd087dd8e38/hardware-installer/verify_user_flipper_bundle.py" \
  -o verify_user_flipper_bundle.py

python3 verify_user_flipper_bundle.py \
  "FlipperAI_ESP32_Complete_Flash_Candidate_UNTESTED.zip" \
  --expect-source 5501cb9b9205a87bec79e7810103a4757a8bb665 \
  --extract-flipper "$HOME/flipper-ai-preview/verified-flipper"
~~~

Expected: a VERIFIED output and one native Flipper update, named flipper-z-f7-update-*.tgz, under verified-flipper. The validator does not connect to or change a Flipper, ESP32, or Android app.

## Before *any* actual firmware flash

- Make an independent backup of the working Momentum firmware, Flipper SD data and settings; verify a qFlipper recovery method.
- Confirm the physical device is a Flipper Zero F7, charged, and that you can recover it if the candidate fails.
- Preserve the currently installed Android AI Satellite and local model data. APK update signing is not yet stable, and the Android BLE fix still needs physical validation.
- Use **only** the validated inner flipper-z-f7-update-*.tgz for an eventual native Flipper F7 updater procedure. Neither the encrypted .enc file nor any of the outer or combined ZIPs are flashable update images.
- ESP32_WROOM32 image files are for a **separate chip** and must not be flashed until the exact board, flash capacity, flash offsets, BOOT/EN wiring and power are independently verified.
- The separate esp_flasher.fap is an optional GPL app that requires user confirmation for writes and matching Momentum SDK. It is not the integrated ESP32 Manager.
- The integrated AUTO transport selection still observes verified BLE only; real Wi-Fi/USB AI handoff is not completed.

**Status:** ready for controlled preparation and archive extraction tests. Hardware flashing and device-level regression validation remain outstanding.
