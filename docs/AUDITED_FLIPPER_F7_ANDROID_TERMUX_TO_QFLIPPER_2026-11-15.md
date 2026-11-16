# New audited Flipper AI Momentum F7 update — simple Android extraction

**Build:** PASSED all GitHub CI checks. **Hardware flash:** NOT YET TESTED. The original working Flipper firmware is not modified by these commands.

## Use this artifact, not the ESP32 ZIP

[GitHub Actions — passed audited F7 native build #43782149547](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43782149547)

Select the **Artifacts** entry named:

**encrypted-flipper-ai-esp32-integration-preview-tgz-UNTESTED**

- Artifact ID: 14189530383
- Size: about 12.7 MB
- Exact ZIP digest reported by GitHub: e7990b391a3959de297fd3df64cebe5ba070de74556cc9f1ad5539bbd80d0718 (SHA-256)
- Expires: November 22, 2026 around 7:52 p.m. Toronto time (2026-11-23T00:51:58Z)
- Private firmware source revision: 642e267612f1c555c60eb0db2ec167f5d2ab036f
- Original Momentum source revision: d3f89dfe2ef6b01839201598e9be1590cba80322

**Avoid the other similarly named artifact**: encrypted-FlipperAI-ESP32-GATT-AUDITED-NEXT-FLASH-CANDIDATE-UNTESTED. That is a *combined* Flipper + ESP32 archive. It requires extra unpacking and risks confusing two different chips' firmware.

On your Samsung browser, download the native-only artifact ZIP from the GitHub Actions run to **Internal storage > Download**. You can leave the Actions ZIP unopened. If Samsung My Files has already unpacked it, the tool also accepts its single \`flipper-ai-native-tgz-delivery.tar.gz.enc\` file.

## 1. Prepare Termux

Paste **one whole command block** at a time, pressing the Enter/Return key after each block:

~~~sh
pkg install -y python openssl-tool curl
termux-setup-storage
mkdir -p "$HOME/flipper-ai-tools"
cd "$HOME/flipper-ai-tools"
~~~

Allow Android storage permission when prompted. If you already granted it, the storage setup command is harmless.

## 2. Download the reviewed, CI-tested phone extractor

These are **public scripts only**; they contain **no firmware, tokens, decryption keys or passwords**. Both source files are pinned to the exact commit that [passed the synthetic extraction tests](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43784385426).

~~~sh
cd "$HOME/flipper-ai-tools"
curl -fL --retry 2 "https://raw.githubusercontent.com/cruefan94/Flipper-AI-Integration-Testing/099e36509814ed975d17b108124f1a0c36a907b7/termux/firmware_to_phone.py" -o firmware_to_phone.py
curl -fL --retry 2 "https://raw.githubusercontent.com/cruefan94/Flipper-AI-Integration-Testing/099e36509814ed975d17b108124f1a0c36a907b7/termux/audited_f7_to_downloads.py" -o audited_f7_to_downloads.py
python -m py_compile firmware_to_phone.py audited_f7_to_downloads.py
~~~

If any \`curl\` command fails, stop. Don't run an older saved script under the same name without checking which one it is.

## 3. Run verification and extraction

~~~sh
cd "$HOME/flipper-ai-tools"
python audited_f7_to_downloads.py
~~~

This command searches both Android shared Downloads and \`~/downloads\` in Termux for the **exact** native artifact ZIP; if needed it can instead use a single extracted \`.tar.gz.enc\`.

You will see:

- INPUT: [exact found path]
- Checking exact GitHub Actions artifact ZIP SHA-256...
- GitHub artifact ZIP digest: VERIFIED (when using original downloaded ZIP)
- **Artifact passphrase (VISIBLE):** paste your privately held artifact passphrase using Samsung keyboard Clipboard or long-press > Paste; press Enter.

**Visible means visible**: anyone watching your phone or a screen recording can read it. Do not screenshot or send the passphrase. To use hidden input instead, run:

~~~sh
python audited_f7_to_downloads.py --hide-passphrase
~~~

This is the same GitHub **FLIPPER_ARTIFACT_PASSPHRASE** encryption secret used for build #43782149547, not your GitHub account password. GitHub will not reveal an existing saved secret. The script checks common copied trailing newline variants and does **not** send a passphrase to GitHub.

The script verifies:

1. GitHub artifact ZIP SHA-256 and exact ZIP inventory (when original outer ZIP is selected)
2. OpenSSL AES-256-CBC / PBKDF2 decryption using the secret kept on your device
3. Exactly pinned private Flipper source revision
4. Native Flipper Zero F7 updater manifest, \`Target: 7\`, \`Loader: updater.bin\`, \`Firmware: firmware.dfu\`
5. Per-file SHA-256 manifest and native \`.tgz\` checksum; no symlink/archive traversal
6. Exclusive file creation so an existing, different Downloads file is **never overwritten**

When successful, the output will explicitly show **SOURCE REVISION: VERIFIED**, **F7 UPDATER SHA256**, **EXACT PATH** and **SUCCESS**. If any check fails, **STOP** and do not flash.

If Samsung renamed the outer ZIP or you have multiple copies, locate the exact files:

~~~sh
find "$HOME/storage/downloads" "$HOME/downloads" -type f \( -iname "*esp32-integration-preview-tgz*.zip" -o -name "flipper-ai-native-tgz-delivery.tar.gz.enc" \) -print 2>/dev/null
~~~

Then rerun with the *actual* full location returned, in double quotes (example only):

~~~sh
python audited_f7_to_downloads.py --input "$HOME/storage/downloads/encrypted-flipper-ai-esp32-integration-preview-tgz-UNTESTED.zip"
~~~

A manually renamed outer ZIP must be restored to the expected original filename (or select the inner \`.tar.gz.enc\`), and its GitHub SHA-256 still must match.

## 4. Find the actual F7 update

The tool puts **only** the verified native Flipper firmware file directly into:

**Samsung My Files → Internal storage → Download**

It is named \`flipper-z-f7-update-*.tgz\`. For a visible filename, size, and exact path, paste:

~~~sh
find "$HOME/storage/downloads" -maxdepth 1 -type f -name "flipper-z-f7-update-*.tgz" -exec ls -lh {} \; 2>/dev/null
~~~

Do **not** flash any \`.zip\`, \`.enc\`, combined firmware ZIP, ESP32 \`.bin\` or outer delivery \`.tar.gz\` file. Only the verified native F7 \`.tgz\` is an update candidate.

## 5. Controlled hardware test only after backup

Your last official Android **Bluetooth** update upload stopped at approximately **7%**, and the original first Flipper AI Momentum build remained fully functional. This is a reported interrupted mobile transfer, **not** proof of a failed native firmware image.

Prefer a **USB-C data cable + Raspberry Pi 4B with qFlipper** for the next attempt:

- Before trying, make a separate backup of the current working Flipper SD data and confirm you can recover/reflash the known-good build.
- Confirm the Flipper battery is charged and qFlipper actually recognizes the device over a *data-enabled* USB cable.
- Move the verified native F7 \`.tgz\` from the Samsung Downloads folder to your Raspberry Pi; select the appropriate custom update-from-file option in qFlipper if supported by your installed version.
- Do not erase, format, put the working unit in recovery mode, install a second Android debug APK, or flash ESP32 simultaneously.
- Only report success once Momentum boots and the Flipper AI app, stock functions, authenticated BLE GATT and AI1 chat have been checked on the actual hardware.

CI compilation, encrypted-delivery integrity and host tests are **PASS**; physical compatibility and mobile BLE firmware-transfer reliability remain **UNVERIFIED**. Keep the original working image as your rollback candidate.
