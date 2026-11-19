#!/usr/bin/env python3
"""Public-safe release-evidence schema gate for non-AI OmniCore (stdlib only).

Run with PRIVATE evidence JSON locally inside a private CI job. Never upload,
post, or print those private files in the public repository. Public CI runs
synthetic tests only. This gate is not a firmware or hardware safety audit.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re

REQUIRED_APPS = frozenset({
    "tag_ident", "nfc_compare", "rfsurvey", "hermes",
    "flip_rpi", "unitemp", "i2c_tools_cli",
})
SHA_RE = re.compile(r"[0-9a-f]{64}\Z")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(build: dict, embedded: dict, resources: dict, staged: dict) -> dict:
    """Validate report consistency; never expose any fields from the input."""
    require(all(isinstance(x, dict) for x in (build, embedded, resources, staged)),
            "Evidence JSON must contain four objects")
    require(build.get("resources_verified") is True
            and build.get("complete_resources_verified") is True,
            "Private complete-resource build gate not passed")
    require(isinstance(build.get("sha256"), str)
            and SHA_RE.fullmatch(build["sha256"]) is not None,
            "No recognized updater digest")
    require(build.get("size", 0) > 100_000
            and isinstance(build.get("source_sha"), str)
            and SHA_RE.fullmatch(build["source_sha"]) is not None,
            "Missing private exact-build provenance")
    require("NOT FLASH APPROVED" in str(build.get("status", "")),
            "Build must remain unapproved")

    require(embedded.get("first_flash_preload_integrity_verified") is True
            and embedded.get("device_tested") is False
            and embedded.get("flash_approved") is False,
            "Embedded resource report is missing required hold")
    require(embedded.get("updater_sha256") == build["sha256"],
            "Private updater digest reports disagree")
    require(embedded.get("embedded_asset_pack_choices") >= 48
            and embedded.get("embedded_ir_profiles", 0) > 0,
            "Expected visual/IR preloads not represented")
    apps = embedded.get("embedded_optional_apps")
    require(isinstance(apps, dict) and REQUIRED_APPS.issubset(apps),
            "An optional source-compiled application is missing")
    for name in REQUIRED_APPS:
        meta = apps[name]
        require(isinstance(meta, dict)
                and meta.get("bytes", 0) >= 1024
                and isinstance(meta.get("path"), str)
                and meta["path"].startswith("apps/")
                and meta["path"].endswith("/" + name + ".fap")
                and isinstance(meta.get("sha256"), str)
                and SHA_RE.fullmatch(meta["sha256"]) is not None,
                "Compiled app metadata invalid")
    require("flipper_ai" not in apps,
            "Non-AI package contains an AI app")

    require(resources.get("full_native_resource_tree_match") is True
            and resources.get("flash_approved") is False
            and resources.get("device_tested") is False
            and resources.get("missing_resources") == 0
            and resources.get("extra_resources") == 0
            and resources.get("hash_mismatches") == 0,
            "Original FBT native-resource comparison failed")
    require(resources.get("files_byte_for_byte_verified", 0) >= 1000
            and resources.get("files_byte_for_byte_verified") == build.get("resource_file_count"),
            "Complete native resource inventory is inconsistent")
    require(resources.get("compiled_faps_including_original_momentum", 0) >= len(REQUIRED_APPS)
            and resources.get("compiled_faps_including_original_momentum") == build.get("installed_fap_count"),
            "Original Momentum app count is inconsistent")

    require(staged.get("asset_choices") == 48
            and staged.get("device_tested") is False
            and staged.get("flash_approved") is False,
            "Staged inputs are not verified non-AI candidates")
    staged_apps = staged.get("apps")
    require(isinstance(staged_apps, dict) and REQUIRED_APPS.issubset(staged_apps),
            "Staged app list incomplete")
    require("flipper_ai" not in staged_apps,
            "AI app unexpectedly staged")
    for name in REQUIRED_APPS:
        source = staged_apps[name]
        require(isinstance(source, dict)
                and isinstance(source.get("revision"), str)
                and SHA_RE.fullmatch(source["revision"]) is not None,
                "Missing pinned source revision")
    return {
        "metadata_gate": "passed",
        "real_f7_build_independently_verified": False,
        "real_hardware_tested": False,
        "flash_approved": False,
        "public_release_allowed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", required=True, type=Path)
    parser.add_argument("--embedded", required=True, type=Path)
    parser.add_argument("--resources", required=True, type=Path)
    parser.add_argument("--staged", required=True, type=Path)
    args = parser.parse_args()
    records = tuple(json.loads(p.read_text(encoding="utf-8"))
                    for p in (args.build, args.embedded, args.resources, args.staged))
    try:
        result = validate(*records)
    except (TypeError, ValueError, KeyError):
        raise SystemExit("FAIL: non-AI release metadata gate (no input details printed)")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
