"""Public-safe release metadata gate. Does not inspect firmware or APK bytes.

Accepts only fixed, non-sensitive evidence fields. Never publish private SHAs
if your repository's policy treats them as confidential; use private tracker.
"""
import json
import re
import sys

SHA256 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
ALLOWED = {"schema_version", "deliverable", "repository", "source_commit",
           "workflow_run_url", "artifact_id", "artifact_sha256",
           "contract_version", "build_ci_passed", "package_verified",
           "hardware_verified", "owner_approved", "status"}
DELIVERABLES = {"android_test_apk", "f7_encrypted_updater"}
STATES = {"hold", "test_only", "ready_for_owner_review"}

def validate(data):
    if not isinstance(data, dict):
        raise ValueError("metadata must be an object")
    unknown = set(data) - ALLOWED
    if unknown:
        raise ValueError("unapproved metadata fields: " + ", ".join(sorted(unknown)))
    required = ALLOWED - {"contract_version"}
    if required - set(data):
        raise ValueError("missing fields: " + ", ".join(sorted(required-set(data))))
    if data["schema_version"] != 1 or data["deliverable"] not in DELIVERABLES:
        raise ValueError("invalid schema or deliverable")
    if data["repository"] not in {"cruefan94/Flipper-AI-Momentum-",
                                  "cruefan94/Flipper-AI-Android-Satellite"}:
        raise ValueError("unexpected source repository")
    if not HEX40.fullmatch(str(data["source_commit"])):
        raise ValueError("source commit must be a full 40-character SHA")
    if not SHA256.fullmatch(str(data["artifact_sha256"])):
        raise ValueError("artifact sha256 must be lowercase hex")
    if not isinstance(data["artifact_id"], int) or isinstance(data["artifact_id"], bool) or data["artifact_id"]<=0:
        raise ValueError("artifact ID must be positive integer")
    if not re.fullmatch(r"https://github\.com/cruefan94/Flipper-AI-(?:Momentum-|Android-Satellite|Integration-Testing)/actions/runs/[1-9][0-9]*",str(data["workflow_run_url"])):
        raise ValueError("run URL must point to approved GitHub Actions repository")
    for key in ("build_ci_passed", "package_verified", "hardware_verified", "owner_approved"):
        if type(data[key]) is not bool:
            raise ValueError(key + " must be boolean")
    if data["status"] not in STATES:
        raise ValueError("invalid status")
    if data["status"]=="ready_for_owner_review" and not (data["build_ci_passed"] and data["package_verified"]):
        raise ValueError("cannot promote unverified package")
    if data["deliverable"]=="f7_encrypted_updater" and data["status"]!="hold" and not data["owner_approved"]:
        raise ValueError("F7 candidate must remain on hold without explicit approval")
    if data.get("contract_version") is not None and not re.fullmatch(r"[A-Za-z0-9._-]{1,32}",str(data["contract_version"])):
        raise ValueError("invalid contract version")
    return True

def main():
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python3 public_safe_release_gate.py metadata.json")
    with open(sys.argv[1],encoding="utf-8") as stream:
        data=json.load(stream)
    validate(data)
    print("Public-safe metadata schema PASS (not artifact integrity or hardware verification)")

if __name__=="__main__": main()
