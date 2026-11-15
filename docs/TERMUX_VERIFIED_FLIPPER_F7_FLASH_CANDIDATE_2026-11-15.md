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

4. **Visible, paste-enabled passphrase input (user preference):** Use the same private `FLIPPER_ARTIFACT_PASSPHRASE` that encrypted the CI artifact. GitHub Secrets cannot show a previously saved value. The following commands visibly echo pasted input in Termux, rather than hiding it. **This is less private than hidden input:** anyone viewing your screen, screen recording, terminal scrollback or screenshot could read it. Use only somewhere private, never post the password, and clear the display afterward.

Long-press the Termux input area and select **Paste**, or use the Android keyboard Clipboard button. Paste at the `Passphrase (VISIBLE):` prompt, then press Enter. The passphrase is supplied through stdin, **not** embedded in shell history or OpenSSL command arguments.

~~~sh
cd "$HOME/flipper-ai-preview"
printf '%s\\n' 'Paste your encryption passphrase below (VISIBLE on screen).'
IFS= read -r -p 'Passphrase (VISIBLE): ' FLIPPER_PASS
if [ -z "$FLIPPER_PASS" ]; then
  printf '%s\\n' 'Empty passphrase; stopping.'
else
  printf '%s\\n' "$FLIPPER_PASS" | openssl enc -d -aes-256-cbc -pbkdf2 -iter 250000 -salt \
    -pass stdin \
    -in "FlipperAI_ESP32_Complete_Flash_Candidate_UNTESTED.zip.enc" \
    -out "FlipperAI_ESP32_Complete_Flash_Candidate_UNTESTED.zip"
fi
unset FLIPPER_PASS
~~~

If decryption fails, stop. Delete the incomplete decrypted ZIP before retrying; **do not flash** a partially written file. If visible input isn't appropriate, the normal OpenSSL command without `-pass stdin` prompts privately with hidden input instead. An unavailable passphrase requires a fresh encrypted build using a known, securely held passphrase.

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

6. **Always find, display and copy the verified native `.tgz` to Android Downloads** so it is visible in **Samsung My Files → Internal storage → Download**. Copying is an explicit step, not a firmware flash. The commands refuse an absent/multiple-file match and do not overwrite an existing same-name Downloads file:

~~~sh
termux-setup-storage
shopt -s nullglob
updates=( "$HOME"/flipper-ai-preview/verified-flipper/flipper-z-f7-update-*.tgz )
if [ "${#updates[@]}" -ne 1 ]; then
  printf '%s\\n' 'STOP: expected exactly one verified .tgz; see files below:'
  find "$HOME/flipper-ai-preview" -maxdepth 3 -type f -name '*.tgz' -print
else
  src="${updates[0]}"
  dest="$HOME/storage/downloads/$(basename "$src")"
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    printf 'Already exists in Downloads (not overwritten): %s\\n' "$dest"
  else
    cp -- "$src" "$dest"
    printf 'COPIED TO ANDROID DOWNLOADS: %s\\n' "$dest"
  fi
  ls -lh -- "$src" "$dest"
fi
~~~

If no `.tgz` appears, rerun the verifier and resolve its error; do **not** copy a similarly named encrypted or unverified file. Show this final location command after **every future Termux extraction**:

~~~sh
find "$HOME/flipper-ai-preview" "$HOME/storage/downloads" -type f -name 'flipper-z-f7-update-*.tgz' -print 2>/dev/null
~~~

**Default for future Flipper AI Termux extraction guides:** give one copy-friendly block at a time; show extraction/decryption progress and exact result; enable visible password paste *when the user specifically wants it* with the screen-privacy warning; automatically include verification plus the Downloads copy and locate steps.

## Before *any* actual firmware flash

- Make an independent backup of the working Momentum firmware, Flipper SD data and settings; verify a qFlipper recovery method.
- Confirm the physical device is a Flipper Zero F7, charged, and that you can recover it if the candidate fails.
- Preserve the currently installed Android AI Satellite and local model data. APK update signing is not yet stable, and the Android BLE fix still needs physical validation.
- Use **only** the validated inner flipper-z-f7-update-*.tgz for an eventual native Flipper F7 updater procedure. Neither the encrypted .enc file nor any of the outer or combined ZIPs are flashable update images.
- ESP32_WROOM32 image files are for a **separate chip** and must not be flashed until the exact board, flash capacity, flash offsets, BOOT/EN wiring and power are independently verified.
- The separate esp_flasher.fap is an optional GPL app that requires user confirmation for writes and matching Momentum SDK. It is not the integrated ESP32 Manager.
- The integrated AUTO transport selection still observes verified BLE only; real Wi-Fi/USB AI handoff is not completed.

**Status:** ready for controlled preparation and archive extraction tests. Hardware flashing and device-level regression validation remain outstanding.
