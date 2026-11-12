# Free-first unified development workflow

The project does not require an external paid AI API for source changes or CI.

## Development sequence

1. Implement firmware and Android features in their respective repositories.
2. Run public, source-safe integration contract tests on every push.
3. Record immutable firmware and Android commit SHAs and evidence URLs.
4. Run `python scripts/verify_release_readiness.py <report.json>` before any release claim.
5. Require physical Flipper-to-Android BLE validation and installation checks before calling the release ready.

## Optional AI

The manual AI workflow defaults to `mock` (no network, no charges).
`groq_free` is opt-in only and may fail due to provider restrictions.
Never automatically retry a failed free-tier request through a paid provider.
The `external` provider is opt-in and may incur charges; it is not needed for development.

## Current release blockers

The Android AI runtime, Momentum firmware integration, physical BLE interoperability,
and installable end-to-end package have not been verified as a complete system.
Passing contract tests alone does not establish hardware readiness.
