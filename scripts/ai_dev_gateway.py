"""Provider-independent, opt-in development AI gateway (Python standard library).

Never executes model output or performs repository writes. Only sends user-supplied prompts.
"""
import json
import os
from urllib import request, error
from urllib.parse import urlsplit

class GatewayError(RuntimeError):
    pass

def _endpoint(url, allow_http_local):
    parts = urlsplit(url)
    if parts.username or parts.password or parts.fragment or parts.query:
        raise GatewayError("Endpoint must not contain credentials, query or fragment")
    local = parts.hostname in ("localhost", "127.0.0.1", "::1")
    if parts.scheme != "https" and not (allow_http_local and local and parts.scheme == "http"):
        raise GatewayError("HTTPS required (HTTP only for explicitly enabled localhost)")
    if not parts.netloc:
        raise GatewayError("Missing endpoint host")
    return url

class Gateway:
    def __init__(self, config, transport=None):
        self.config = config
        self.transport = transport or self._post

    @staticmethod
    def _post(url, headers, payload, timeout):
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(url, data=data, headers=headers, method="POST")
        try:
            with request.urlopen(req, timeout=timeout) as response:
                raw = response.read(1024 * 1024 + 1)
                if len(raw) > 1024 * 1024:
                    raise GatewayError("Response too large")
                return json.loads(raw.decode("utf-8"))
        except error.HTTPError as exc:
            # Only report recognized machine-readable codes, never provider messages.
            safe_codes = {"model_not_found", "model_permission_denied", "permission_denied",
                          "invalid_api_key", "authentication_error", "insufficient_quota",
                          "rate_limit_exceeded", "organization_restricted", "access_denied"}
            detail = ""
            try:
                body = json.loads(exc.read(4096).decode("utf-8"))
                problem = body.get("error", {})
                code = problem.get("code") if isinstance(problem, dict) else None
                if isinstance(code, str) and code in safe_codes:
                    detail = f" ({code})"
                elif exc.code == 403:
                    message = problem.get("message", "") if isinstance(problem, dict) else ""
                    if isinstance(message, str):
                        low = message.lower()
                        if any(word in low for word in ("country", "region", "location")):
                            detail = " (geographic restriction)"
                        elif "organization" in low:
                            detail = " (organization restriction)"
                        elif any(word in low for word in ("model", "permission")):
                            detail = " (model or permission restriction)"
                        elif "ip address" in low:
                            detail = " (IP restriction)"
                        elif any(word in low for word in ("blocked", "restricted")):
                            detail = " (access restriction)"
            except (ValueError, UnicodeError, AttributeError, TypeError):
                pass
            raise GatewayError(f"Provider HTTP status {exc.code}{detail}; check provider permissions or access policy") from None
        except (error.URLError, ValueError, UnicodeError) as exc:
            raise GatewayError("Provider connection or response failed") from None

    def ask(self, prompt, provider=None):
        if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 20000:
            raise GatewayError("Prompt must contain 1-20000 characters")
        name = provider or self.config.get("default_provider", "mock")
        providers = self.config.get("providers", {})
        if name not in providers:
            raise GatewayError("Unknown provider")
        spec = providers[name]
        kind = spec.get("kind")
        if kind == "mock":
            return {"provider": name, "answer": "MOCK: no AI request was sent", "simulated": True}
        if kind != "openai_compatible":
            raise GatewayError("Unsupported provider kind")
        if os.environ.get("FLIPPER_AI_DEV_NETWORK") != "1":
            raise GatewayError("Network AI disabled; explicitly set FLIPPER_AI_DEV_NETWORK=1")
        url = _endpoint(spec.get("endpoint", ""), spec.get("allow_http_local", False))
        key_env = spec.get("api_key_env")
        key = os.environ.get(key_env, "") if key_env else ""
        if spec.get("requires_api_key", True) and not key:
            raise GatewayError("Missing provider API key environment variable")
        headers = {"Content-Type": "application/json"}
        if key:
            headers["Authorization"] = "Bearer " + key
        payload = {"model": spec["model"], "messages": [{"role": "user", "content": prompt}], "stream": False}
        response = self.transport(url, headers, payload, min(max(int(spec.get("timeout_seconds", 30)), 1), 120))
        try:
            answer = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise GatewayError("Malformed provider response") from exc
        if not isinstance(answer, str):
            raise GatewayError("Provider returned non-text content")
        return {"provider": name, "answer": answer, "simulated": False}
