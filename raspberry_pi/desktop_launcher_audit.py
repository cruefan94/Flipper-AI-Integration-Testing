#!/usr/bin/env python3
"""Read-only, offline XDG .desktop launcher audit. Never executes launchers."""
import argparse
import configparser
import json
import os
from pathlib import Path
import re
import shutil

FIELD_CODE = re.compile(r"%[fFuUdDnNickvm]")
SHELL_META = re.compile(r"[|;&<>\x60]")
DEFAULT_DIRS = ("/usr/share/applications", "/usr/local/share/applications")

def audit_file(path, which=shutil.which):
    parser = configparser.ConfigParser(interpolation=None, strict=False)
    parser.optionxform = str
    try:
        with path.open(encoding="utf-8-sig") as handle:
            parser.read_file(handle)
        if not parser.has_section("Desktop Entry"):
            return {"file": path.name, "status": "invalid", "reason": "missing Desktop Entry"}
        entry = parser["Desktop Entry"]
        name = entry.get("Name", path.stem)
        command = entry.get("Exec", "").strip()
        if entry.get("Type", "Application") != "Application":
            return {"file": path.name, "name": name, "status": "not_application"}
        if entry.get("Hidden", "false").lower() == "true":
            return {"file": path.name, "name": name, "status": "hidden"}
        # XDG TryExec controls whether a launcher should be shown by the desktop.
        # Check it without running anything, before checking the main Exec command.
        try_exec = entry.get("TryExec", "").strip()
        if try_exec:
            if SHELL_META.search(try_exec) or any(ch.isspace() for ch in try_exec):
                return {"file": path.name, "name": name, "status": "review_tryexec"}
            try_path = Path(try_exec)
            found = (try_path.is_file() and os.access(try_path, os.X_OK)
                     if "/" in try_exec else which(try_exec) is not None)
            if not found:
                return {"file": path.name, "name": name, "status": "missing_tryexec"}
        if not command:
            return {"file": path.name, "name": name, "status": "missing_exec"}
        # Avoid shell parsing/execution: only inspect first executable token.
        import shlex
        try:
            tokens = shlex.split(command)
        except ValueError:
            return {"file": path.name, "name": name, "status": "invalid_exec"}
        if not tokens:
            return {"file": path.name, "name": name, "status": "missing_exec"}
        executable = FIELD_CODE.sub("", tokens[0])
        if executable == "env":
            # Environment-variable launchers need manual review; do not guess.
            return {"file": path.name, "name": name, "status": "review_wrapper"}
        if SHELL_META.search(executable):
            return {"file": path.name, "name": name, "status": "review_wrapper"}
        exists = (Path(executable).is_file() if "/" in executable else which(executable) is not None)
        return {"file": path.name, "name": name, "status": "executable_found" if exists else "missing_executable"}
    except (OSError, UnicodeError, configparser.Error) as exc:
        return {"file": path.name, "status": "unreadable", "reason": type(exc).__name__}

def scan(directories):
    entries = []
    for directory in directories:
        try:
            entries.extend(audit_file(path) for path in sorted(Path(directory).glob("*.desktop")) if path.is_file())
        except OSError:
            continue
    return sorted(entries, key=lambda x: (x["file"], x["status"]))

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--directory", action="append", help="Directory containing desktop entries (repeatable)")
    ap.add_argument("--json", action="store_true", help="Machine-readable output; inspect before sharing")
    args = ap.parse_args()
    dirs = args.directory or [*DEFAULT_DIRS, str(Path.home()/".local/share/applications")]
    rows = scan(dirs)
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        for row in rows:
            print(f'{row["status"]:20} {row["file"]}')
        print(f"Audited {len(rows)} entries. No applications were launched or changed.")
if __name__ == "__main__":
    main()
