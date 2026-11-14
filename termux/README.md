# Flipper AI - Termux command bridge (prototype)

This is an opt-in GitHub Issues command bridge for Android Termux, NOT direct ChatGPT access to the phone.
Commands are submitted to issues in the **private** cruefan94/Flipper-AI-Momentum- repository.
The Termux process polls private issues and reports results as private issue comments.

**STATUS: NOT TESTED ON THE PHONE.** No automatic installation, firmware flashing, or elevated permissions.

## One-time setup on the phone

Install up-to-date Termux from F-Droid or the official Termux GitHub releases. Then open Termux:

~~~sh
pkg update
pkg install -y python git gh curl
gh auth login --hostname github.com --git-protocol https --web
mkdir -p "$HOME/.flipper-ai-termux"
curl -fLsS "https://raw.githubusercontent.com/cruefan94/Flipper-AI-Integration-Testing/main/termux/termux_bridge.py" -o "$HOME/.flipper-ai-termux/termux_bridge.py"
python "$HOME/.flipper-ai-termux/termux_bridge.py" watch
~~~

Authenticate with an account that can access **private** cruefan94/Flipper-AI-Momentum- issues.
Never paste authentication tokens into chats or public repositories.
The bridge polls every 30 seconds while running, but Android can suspend background processes.

Inspect without starting the watcher:

~~~sh
python "$HOME/.flipper-ai-termux/termux_bridge.py" status
~~~

Poll once instead of continuously:

~~~sh
python "$HOME/.flipper-ai-termux/termux_bridge.py" once
~~~

## Private GitHub command format

Create a private issue titled [Termux] Diagnostics whose body consists only of JSON:

~~~json
{"schema":1,"device":"phone","operation":"diagnostics","args":{}}
~~~

Other supported read-only actions: repo_status with a repo alias and workflow_runs with a repo alias.
Aliases are momentum, android, testing. Local clone paths are under ~/flipper-ai-workspace/.
These commands do NOT automatically clone repositories.

Arbitrary command example (requires explicit local approval):

~~~json
{"schema":1,"device":"phone","operation":"shell","args":{"command":"pwd","cwd":"home"}}
~~~

After the request is fetched, Termux prints the issue number. Approve its exact command locally:

~~~sh
python "$HOME/.flipper-ai-termux/termux_bridge.py" approve 123
~~~

Replace 123 with the real issue number and enter YES after reviewing the exact command.
Unapproved shell requests do not run. Local approval is necessary again for each new shell request.
The bridge checks whether the issue is still open and unchanged before running a shell command.

Results appear as a comment on the **private** issue, which is then closed.
Output filtering is best-effort only: do not run commands that print secrets or private personal data.

## Boundaries and release safety

- GitHub CLI permissions are used only inside Termux; no public inbound server or privileged device access.
- Only issues created by owner cruefan94, matching device phone and schema 1, are considered.
- Any approved shell command inherits Termux user permissions; approve carefully.
- At-most-once execution is attempted with local state markers, but failures still require manual review.
- Automatic firmware flashing and recovery are not implemented or recommended.
- Do not use the public testing repository as a private output or private command queue.
- To stop watching use Ctrl+C; to revoke GitHub CLI authentication use gh auth logout.

## Validation sequence

1. Run status and gh auth status on the phone.
2. Start watch, submit one diagnostics request, and verify its private issue comment.
3. Confirm a shell request cannot run without local approval.
4. Approve harmless pwd, verify correct response, and check restart behavior.
5. Check output for secrets before enabling any other development operations.

## Prepare verified firmware on Android (no automatic flashing)

The opt-in `firmware_to_phone.py` helper downloads the **latest successful custom Momentum AI firmware** artifact from GitHub, prompts locally for the existing firmware-artifact passphrase, checks the native F7 update archive and its file hashes, then saves the original `flipper-z-f7-update-*.tgz`. Nothing is uploaded from the phone and **nothing is flashed**.

In an **interactive Termux session**, with the phone charged and GitHub CLI already authenticated:

~~~sh
pkg install -y openssl
curl -fLsS "https://raw.githubusercontent.com/cruefan94/Flipper-AI-Integration-Testing/main/termux/firmware_to_phone.py" -o "$HOME/.flipper-ai-termux/firmware_to_phone.py"
python "$HOME/.flipper-ai-termux/firmware_to_phone.py"
~~~

Output stays private at `~/flipper-ai-workspace/firmware-updates/` by default. To copy the **verified** native update file into Android Downloads for a supported app's file picker, first approve `termux-setup-storage` locally, then use `python "$HOME/.flipper-ai-termux/firmware_to_phone.py" --share-downloads`. An explicit `--run-id` can select a particular successful **main-branch** firmware run, if that encrypted artifact has not expired.

**The private artifact passphrase is not retrievable from the GitHub Actions secret.** If you don't know it, reset `FLIPPER_ARTIFACT_PASSPHRASE` in GitHub Actions repository secrets and run a new firmware build. **Never send the passphrase into chat, a GitHub issue, or a command-line argument.** Run this tool *locally with a visible prompt*, not from the remote bridge's noninteractive approved shell operation.

This helper is not a release endorsement. It checks archive integrity and that the package targets Flipper Zero F7, not whether the experimental AI firmware boots. Have a known-good Momentum update and a confirmed qFlipper/DFU recovery method before choosing to flash the native `.tgz`. The firmware itself remains experimental and hardware-untested.
