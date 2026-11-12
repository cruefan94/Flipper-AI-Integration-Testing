"""Redact common credential forms from public AI development prompts."""
import re

PATTERNS = (
    re.compile(r"(?i)(?:api[_ -]?key|access[_ -]?token|password|secret)\s*[:=]\s*[^\s,;]+"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
)

def check_public_prompt(prompt):
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 20000:
        raise ValueError("Prompt must contain 1-20000 characters")
    for pattern in PATTERNS:
        if pattern.search(prompt):
            raise ValueError("Potential credential in prompt; do not submit secrets to public AI workflows")
    return prompt
