# Flipper AI Raspberry Pi 4B Companion — Phone USB Not Required

**Status:** Source implemented; [public synthetic CI passed](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43788578323). **Not yet installed or hardware-tested on the owner's Pi.** No existing Momentum firmware or Android app is changed.

## Purpose

A lightweight Python helper runs directly on Raspberry Pi OS. The Pi can inspect firmware files, check local USB and Bluetooth status, report whether qFlipper is available, and answer diagnostic requests sent through **private GitHub Issues**. The phone and Pi do not need a cable and can even be on different networks, so long as the Pi has internet.

Optional Bluetooth file sharing is supported through the Pi OS Bluetooth/OBEX programs, not implemented by this Python bridge. A separate optional OpenAI API client can answer natural-language questions *on the Pi*. ChatGPT subscription and API usage are billed separately; the GitHub diagnostic bridge needs **no OpenAI API key**.

## 1. Install on the Pi, not Termux

Using the Pi's own keyboard, screen and Terminal:

~~~sh
sudo apt update
sudo apt install -y git gh python3 bluetooth bluez blueman bluez-obexd
git clone https://github.com/cruefan94/Flipper-AI-Integration-Testing.git "$HOME/flipper-ai-pi"
cd "$HOME/flipper-ai-pi"
git checkout feature/raspberry-pi4b-ai-bridge-v01-20261115
python3 raspberry_pi/pi_bridge.py status
~~~

If the folder already exists, don't clone over it. Instead:

~~~sh
cd "$HOME/flipper-ai-pi"
git fetch origin
git checkout feature/raspberry-pi4b-ai-bridge-v01-20261115
python3 raspberry_pi/pi_bridge.py status
~~~

Read-only local diagnostics (nothing is installed or flashed):

~~~sh
python3 raspberry_pi/pi_bridge.py usb
python3 raspberry_pi/pi_bridge.py firmware
~~~

The firmware inventory looks for native Flipper updater .tgz files in the Pi's Downloads and selected Flipper workspace folders. It verifies F7 target and native manifest structure and computes SHA-256. It cannot establish a source revision using the native updater alone.

## 2. Pair the Samsung and Raspberry Pi over Bluetooth for file sharing

On the Pi open Blueman Bluetooth Manager, make the Pi visible, and pair it with the Samsung through Android Bluetooth settings. In Blueman settings, enable incoming file transfers and accept transfers only from devices you trust. Then use Samsung **My Files → Download → choose verified Flipper .tgz → Share → Bluetooth → Raspberry Pi**. Check the Pi's configured Bluetooth receive folder (often ~/Downloads).

**Bluetooth pairing alone does not create an IP connection.** The private GitHub control bridge needs internet on the Pi via home Wi-Fi, the phone's Wi-Fi hotspot, Ethernet or separately configured Bluetooth PAN/tethering. Bluetooth PAN itself has not been hardware-verified.

If Bluetooth file sharing is difficult, skip it: the Pi can download the encrypted GitHub firmware artifact directly using its own internet. You don't have to transfer the file from your phone first.

## 3. Connect the Pi to this project's private GitHub command bridge

Authenticate **on the Pi** with your own GitHub account that can access the private Momentum repository:

~~~sh
gh auth login --hostname github.com --git-protocol https --web
gh auth status
~~~

Never paste your GitHub credentials into ChatGPT or GitHub issue comments. Once login succeeds, start the private watcher:

~~~sh
cd "$HOME/flipper-ai-pi"
python3 raspberry_pi/pi_bridge.py watch
~~~

Leave this Pi terminal open. Ctrl+C stops the watcher. It polls the private firmware repository's Issues every 30 seconds. It accepts only owner-authored issue titles beginning with [Pi] and bodies in this shape:

~~~json
{"schema":1,"device":"raspberrypi4b","operation":"usb_status","args":{}}
~~~

Supported read-only remote commands: diagnostics, usb_status, firmware_inventory, qflipper_status, workflow_runs (repo alias momentum, android or testing). No arbitrary remote shell, automatic update or ESP32 flash operation exists. An optional launch_qflipper request remains pending until you explicitly approve it **on the Pi keyboard**:

~~~sh
python3 raspberry_pi/pi_bridge.py approve 123
~~~

Replace 123 with the actual issue number and type YES only if you want qFlipper opened. It does not flash.

**After installation**, in this ChatGPT conversation ask: "Check my Pi USB connection through the private GitHub bridge." I can create the appropriate private GitHub issue and inspect its returned result after the Pi watcher has run. The Pi process must remain running and have GitHub access. This is not permanent direct control of the Pi by this chat.

## 4. Optional AI assistant directly in Raspberry Pi terminal

A local interactive text assistant can be added using the official OpenAI Python library; it is a separate API client, not your ChatGPT app session. It makes no device changes and does not execute the AI's suggested commands. API service incurs separate usage charges.

~~~sh
sudo apt install -y python3-venv
python3 -m venv "$HOME/flipper-ai-venv"
. "$HOME/flipper-ai-venv/bin/activate"
python -m pip install openai
cd "$HOME/flipper-ai-pi"
read -rs -p "Enter private OpenAI API key (HIDDEN): " OPENAI_API_KEY
echo
export OPENAI_API_KEY
python raspberry_pi/pi_bridge.py ask
unset OPENAI_API_KEY
~~~

The key is required only for this optional local AI question feature. Never enter it into a GitHub issue, a screenshot or chat. Run the ask command with --with-diagnostics only if you explicitly want limited Pi status included in the OpenAI API request.

If you want to use your existing ChatGPT account instead of a separately billed API account, visit https://chatgpt.com in the Raspberry Pi browser. Browser ChatGPT by itself cannot directly operate the Pi's terminal.

## 5. Flipper update by Pi USB, not phone USB

Your phone's last firmware uploads stopped around 7% in the official Flipper Android app, while the original first Momentum AI build continued running. Do not keep retrying over Bluetooth.

Once the Pi bridge is running, connect the **Flipper Zero to the Pi** by a proper USB-C data cable; no phone cable is needed. Run the Pi USB diagnostics, open qFlipper locally, and confirm the Flipper is actually recognized. Back up the known-good firmware, SD data and recovery method before attempting any new update.

Only the verified native Flipper Zero F7 .tgz should be used for the eventual update—not an ESP32 .bin, an encrypted .enc or a combined ZIP. All new firmware remains experimental until actual device boot and functional testing pass.

## Security and limitations

- Public Pi source, **private GitHub issue queue**.
- No local HTTP server or open LAN port.
- No automatic remote shell or flashing/erasing.
- Read-only device metadata and update archive inspection; no device serials or Bluetooth MAC addresses reported to GitHub.
- Optional AI service requires user-set API key and explicit prompt; status is sent to API only with --with-diagnostics.
- qFlipper GUI launch requires owner confirmation on the Pi keyboard.
- Works only once installed and authorized on the physical Pi; CI is not a substitute for device testing.


## 6. Prepare pinned audited newer F7 firmware directly on Pi (no phone transfer)

Once qFlipper recognizes your Flipper and you have a backup, leave the old recovery firmware alone. Run on the Raspberry Pi:

~~~sh
cd "$HOME/flipper-ai-pi"
git pull --ff-only
sudo apt install -y openssl
python3 raspberry_pi/prepare_audited_f7.py
~~~

The pinned helper checks successful GitHub Actions run 43782149547, exact non-expired artifact 14189530383, downloads its encrypted delivery through your logged-in gh CLI, prompts for the privately held ARTIFACT passphrase on the Pi (hidden input; not the GitHub password), checks the exact audited source revision 642e267612f1c555c60eb0db2ec167f5d2ab036f, and verifies each native F7 firmware SHA256 through the pinned public validator.

Verified output is written to ~/FlipperAI_ReadyToFlash/ and neither the original mntm-012 file nor the Flipper device is changed.

Only when the script reports SUCCESS and the source revision/hash verification should you locate the new TGZ under FlipperAI_ReadyToFlash and use qFlipper Advanced controls -> Install from file (custom firmware) if available. Do not use the normal Update Channel control, which selects official channels rather than this audited build. Verify the exact path and filename in the GUI before clicking install.

Because this firmware is not hardware-tested, keep the charged Flipper connected to the Pi with a reliable USB data cable, preserve the backups and recovery TGZ, and confirm a microSD card is inserted. If the file/install control is missing or the artifact has expired/decryption fails, stop rather than attempting a different candidate.

No AI bridge command can flash firmware. This remains a manual and explicitly approved action in qFlipper.