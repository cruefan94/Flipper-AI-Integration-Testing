# Automatic two-failure / billing-blocked CI fallback

## Owner-approved rule (2026-11-13)

**When a core project's GitHub Actions workflow fails two consecutive completed attempts on the same workflow and branch, automatically send that check to the public-safe integration-testing workspace.** A failed workflow with **zero scheduled jobs** is treated as *suspected* billing, disabled Actions, runner provisioning, or pre-job infrastructure failure and is routed after the first occurrence. Do not assert that billing is the verified cause from job count alone.

The goal is an independent runner and contract/build verification before concluding that source code is broken. A public runner pass does **not** mean hardware is working, and a private runner failure does **not** mean the code is broken.

## What is implemented

- `.github/workflows/ci-failover-monitor.yml` checks the **private Momentum firmware** and **public Android Satellite** Actions histories every 30 minutes via public GitHub Actions, as well as on explicit manual dispatch.
- `scripts/ci_failover.py` checks the newest run for each workflow+branch. Success resets the failure streak. Two consecutive **failed completed runs** trigger a fallback. A rerun of the same run counts only when GitHub's previous-attempt API independently reports a failure. A failure with zero jobs routes at once as `suspected_runner_or_billing`.
- Runs newer than four days are considered, with no more than three fallback requests per scan.
- `.github/workflows/ci-fallback-verify.yml` runs only these allowlisted public-side jobs:
  - **firmware:** reuses the existing private-source Momentum CI compiler; checks the native F7 `.tgz` and uploads **only passphrase-encrypted** private firmware (no public plaintext).
  - **protocol:** reuses private-to-public BLE/C/Java host-contract tests with temporary private checkout.
  - **android:** compiles the public Android APK and host tests on an independent public runner; exact public source SHA when possible. A private-repo Android failure instead checks a known public Android baseline, **not** the private source.
  - **contract:** reruns public Cloudflare Worker/AI1 contract tests.
  - **diagnostic:** tests public runner and portable fixtures only. This does **not** reproduce unmapped source builds.
- Deduplication uses the originating `repository#run_id` in the fallback run's GitHub Actions display title, so a scheduled scan does not launch the same fallback repeatedly.
- No source branches or PRs are automatically merged. No flashing, publishing unencrypted private artifacts, deploying cloud Workers, or acting on remote devices.

## Credentials and activation requirements

The public integration-testing repository's workflow needs:
- `GITHUB_TOKEN` (supplied by GitHub) with this repository's Actions **write** permission to dispatch another workflow.
- `FLIPPER_PRIVATE_ACTIONS_READ_TOKEN` (preferred) with GitHub Actions **read** permission for the private `cruefan94/Flipper-AI-Momentum-` repository. The existing `FLIPPER_PRIVATE_SOURCE_TOKEN` can be used only if it already has sufficient Actions-read rights. The Actions-read token should be scoped to the specific repo and read-only; never paste it into chat, source or logs.
- The existing **separate** private source Contents-read token `FLIPPER_PRIVATE_SOURCE_TOKEN` for firmware/protocol fallback builds.
- The existing `FLIPPER_ARTIFACT_PASSPHRASE` for encrypted firmware delivery, never printed or committed.

If the private Actions token is missing or insufficient, the monitor logs a sanitized **warning and skips the private repository**. Public Android monitoring may still work. **Do not call private automatic fallback active until a scheduled/manual monitor run has confirmed access.**

GitHub scheduled workflows run only on the public default branch, may be delayed, can be disabled by the platform and depend on functioning Actions billing/runners in the **public** repository. This is not a separate always-on external service, and it cannot bypass a platform-wide suspension.

## Verification and evidence levels

1. Source and synthetic detector tests pass (routing logic only).
2. GitHub scheduled/manual watcher starts and can read target repo runs (automation active).
3. An eligible failure dispatches the relevant fallback exactly once (integration check).
4. The fallback CI job compiles/runs its bounded host tests (build/contract check).
5. Physical Flipper boot, Android phone inference/BLE, battery effects and flash recovery still require explicit hardware verification.

An encrypted firmware `.tgz` built by fallback is always labeled **UNTESTED** until hardware verification.

## Existing public integration and recovery documentation

- [Momentum native phone updater](PHONE_NATIVE_TGZ_DELIVERY.md)
- [First flash gate](MOMENTUM_FIRST_FLASH_GATE.md)
- [Unified ecosystem map](../PROJECT_ECOSYSTEM.md)

**Side-project scope:** Battery Optimizer, Civic Companion, mascot assets and community variants remain separate and are NOT silently imported, merged, built or deployed by the fallback watcher. The global policy applies to future supported workflows when a reviewed public-safe fallback route is implemented for them.
