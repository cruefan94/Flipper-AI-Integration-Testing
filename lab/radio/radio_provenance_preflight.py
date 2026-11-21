"""Offline, public-safe provenance review for proposed receive-only radio feeds.

This tool does not fetch URLs, contact providers, or establish legal authorization.
It is a conservative metadata preflight; human review is mandatory.
"""
import json
import sys
from urllib.parse import urlsplit


def assess(entry):
    if not isinstance(entry, dict):
        return ["entry_not_object"]
    errors = []
    if entry.get("category") not in {"AM", "FM", "CB", "fire", "police"}:
        errors.append("unsupported_category")
    url = entry.get("source_url")
    if not isinstance(url, str):
        errors.append("missing_url")
    else:
        try:
            parts = urlsplit(url)
            if parts.scheme != "https" or not parts.hostname or parts.username or parts.password or parts.fragment:
                errors.append("unsafe_source_url")
        except ValueError:
            errors.append("unsafe_source_url")
    for field in ("provider_name", "public_listing_url", "reviewed_on", "reviewer_note"):
        if not isinstance(entry.get(field), str) or not entry[field].strip():
            errors.append("missing_" + field)
    if entry.get("receive_only") is not True:
        errors.append("not_receive_only")
    if entry.get("encrypted") is not False:
        errors.append("encrypted_or_unknown")
    if entry.get("access_review") != "human_approved":
        errors.append("human_review_required")
    return errors


def main():
    if len(sys.argv) != 2:
        print("usage: python radio_provenance_preflight.py fixture.json", file=sys.stderr)
        return 2
    with open(sys.argv[1], encoding="utf-8") as f:
        records = json.load(f)
    if not isinstance(records, list):
        print("expected JSON list", file=sys.stderr)
        return 2
    for i, record in enumerate(records):
        errors = assess(record)
        print(json.dumps({"index": i, "preflight": "review_ready" if not errors else "blocked", "reasons": errors}))
    return 1 if any(assess(x) for x in records) else 0


if __name__ == "__main__":
    raise SystemExit(main())
