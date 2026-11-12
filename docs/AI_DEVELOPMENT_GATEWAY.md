# AI development gateway

The development assistant is **separate** from the Flipper Zero's runtime AI. The gateway lets the project switch development providers without changing task callers.

## Default behavior
No AI calls are made unless `FLIPPER_DEV_AI_ENABLED=true`. The default manual provider transmits nothing.

## Opt-in external provider
Configure the following **locally** or using protected CI secrets; never commit credentials:

- `FLIPPER_DEV_AI_ENABLED=true`
- `FLIPPER_DEV_AI_ENDPOINT=https://YOUR-TRUSTED-PROVIDER/v1/chat/completions`
- `FLIPPER_DEV_AI_MODEL=YOUR-MODEL`
- `FLIPPER_DEV_AI_KEY=YOUR-SECRET`

Example (manual invocation; does not modify files):
```python
from scripts.ai_dev_gateway import run_task
print(run_task("Summarize a sanitized CI failure and propose a patch"))
```

Only send sanitized, approved task content. The gateway does not automatically access private repositories, execute generated commands, commit code, or grant GitHub write permissions. Avoid passing source code, tokens, credentials, signing keys or user data to external providers without explicit approval.

## Later replacement with your own AI
Implement `complete(prompt: str) -> str` in a provider backed by the Android AI Satellite or a trusted local bridge. The existing task interface stays unchanged. A phone-local model may require a separate authenticated transport; do not expose an unauthenticated phone endpoint to the internet.

## Next implementation gates
- Provider endpoint allowlist and bounded request/response sizes
- Sanitization/redaction before sending CI excerpts
- Read-only code review and structured patch proposals
- Human-approved commits and pull requests
- AI provider health checks and fallback to manual mode
- Local Android model bridge and hardware integration
