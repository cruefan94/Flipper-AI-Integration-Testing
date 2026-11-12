# GitHub Actions AI development assistant

This public repository provides a **manual, read-only** GitHub Actions workflow at `.github/workflows/manual-ai-dev.yml`. The AI gateway is not a GitHub coding agent and cannot edit repositories or run its output.

## First run without credentials
1. Open **Actions > Manual AI development assistant > Run workflow** on a branch where the workflow is available.
2. Select `mock` and enter a non-sensitive prompt.
3. Download the `ai-development-response` artifact. The mock answer confirms workflow wiring only; it is not AI inference.

## Connect external AI
1. Obtain your own API key from your chosen provider; API usage may be billed separately.
2. In this repository's **Settings > Secrets and variables > Actions**, create a repository secret named `FLIPPER_AI_EXTERNAL_API_KEY`.
3. Select `external` when manually running the workflow. The example uses an OpenAI-compatible chat-completions API; configure model and endpoint in `config/ai_dev_gateway.example.json` if needed.
4. Inspect the response artifact. No automatic commits, PRs, firmware flashing or Android installs occur.

**Public repository warning:** Workflow inputs and downloadable artifacts may be visible to people with access to public Actions data. Submit only public, non-sensitive questions. Never submit private firmware source, API keys, credentials or private logs. Responses are stored for one day. For private development prompts, use a private runner/repository instead.

## Future Flipper AI
The local `flipper_local` provider is available in the gateway for a compatible server. GitHub-hosted runners cannot access an AI server on your phone at `127.0.0.1`; local mode must be run on the same host or connected through a separately authenticated secure endpoint. Switching provider requires no changes to the caller API.

## Verification boundaries
Python gateway unit tests and public integration CI can pass without a real AI service. External inference requires a user-provided secret and a manually dispatched workflow; **it is not verified by the mock tests**. Do not confuse AI-generated recommendations with compiler/test results.
