# Switchable AI development assistant

The development AI gateway is separate from the Android Flipper AI inference engine. It accepts a manually supplied prompt and returns text; it does **not** execute AI-suggested commands, read repositories automatically, commit code, or grant AI GitHub credentials.

## Safe default
From repository root:
```sh
python -m scripts.ask_dev_ai "Review this build error"
```
This uses a deterministic mock response. No network or paid AI calls occur.

## External development AI
Edit `config/ai_dev_gateway.example.json` to select `external` or use `--provider external`. Supply your own authorized API key through an environment variable, never in source:
```sh
export FLIPPER_AI_DEV_NETWORK=1
export FLIPPER_AI_EXTERNAL_API_KEY="your-key"
python -m scripts.ask_dev_ai --provider external "Suggest tests for AI1 BLE framing"
```
This sends the prompt to the configured third-party service and may incur provider charges. Do not send private code, secrets, personal data or credentials unless explicitly authorized and appropriately protected. This project does not provision API keys or external accounts.

## Future own AI
When your Android AI engine exposes an authenticated, OpenAI-compatible chat-completions endpoint, select `flipper_local` and enable networking. The example endpoint uses loopback HTTP for development on the same host; remote access must use HTTPS and authentication. The gateway API remains `Gateway.ask(prompt, provider)`.

## Limits and integration
Provider switching and simulated responses are implemented; **no real external provider request or local Flipper AI server has been verified**. The gateway does not automatically solve build failures or modify GitHub. Its default-deny network setting protects against unintended transmission. Existing CI discovers the Python unit tests under `tests/`. Validate hardware, AI quality, provider credentials, and production endpoint separately.
