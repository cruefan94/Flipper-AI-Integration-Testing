"""Opt-in AI developer provider gateway. No network operations or credentials stored here."""
from dataclasses import dataclass
from typing import Protocol
import os

class DeveloperProvider(Protocol):
    def complete(self, prompt: str) -> str: ...

@dataclass
class ManualProvider:
    """Safe default: no external API calls."""
    def complete(self, prompt: str) -> str:
        return "AI development provider not configured. No code or secrets were transmitted."

class OpenAICompatibleProvider:
    """Uses an OpenAI-compatible HTTPS chat-completions endpoint with explicit opt-in."""
    def __init__(self, endpoint: str, model: str, api_key: str):
        from urllib.parse import urlparse
        parsed = urlparse(endpoint)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
            raise ValueError("An HTTPS endpoint without embedded credentials is required")
        if not endpoint.rstrip("/").endswith("/chat/completions"):
            raise ValueError("Endpoint must end with /chat/completions")
        if not model or not api_key:
            raise ValueError("Model and API key required")
        self.endpoint, self.model, self.api_key = endpoint, model, api_key

    def complete(self, prompt: str) -> str:
        import json
        from urllib.request import Request, urlopen
        body = json.dumps({"model": self.model, "messages": [{"role": "user", "content": prompt}], "stream": False}).encode()
        req = Request(self.endpoint, data=body, headers={
            "Authorization": "Bearer " + self.api_key,
            "Content-Type": "application/json"}, method="POST")
        with urlopen(req, timeout=45) as response:
            result = json.load(response)
        return result["choices"][0]["message"]["content"]

def select_provider(env=None):
    env = os.environ if env is None else env
    if env.get("FLIPPER_DEV_AI_ENABLED") != "true":
        return ManualProvider()
    return OpenAICompatibleProvider(
        env.get("FLIPPER_DEV_AI_ENDPOINT", ""),
        env.get("FLIPPER_DEV_AI_MODEL", ""),
        env.get("FLIPPER_DEV_AI_KEY", ""))

def run_task(prompt: str, env=None):
    if not prompt.strip():
        raise ValueError("Task cannot be empty")
    return select_provider(env).complete(prompt)
