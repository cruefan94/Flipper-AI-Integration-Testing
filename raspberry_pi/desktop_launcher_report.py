#!/usr/bin/env python3
"""Read-only Pi desktop launcher triage; never executes launchers or writes files."""
import argparse
import json
from collections import Counter
from pathlib import Path
from raspberry_pi.desktop_launcher_audit import DEFAULT_DIRS, scan

ATTENTION = frozenset({"invalid", "unreadable", "missing_exec", "invalid_exec",
                       "missing_executable", "missing_tryexec", "review_tryexec", "review_wrapper"})
INFORMATIONAL = frozenset({"hidden", "not_application", "executable_found"})

def summarize(rows):
    counts = Counter(row["status"] for row in rows)
    problems = sorted(({"file": row["file"], "status": row["status"]}
                       for row in rows if row["status"] in ATTENTION),
                      key=lambda row: (row["status"], row["file"]))
    return {"total": len(rows), "attention_count": len(problems),
            "status_counts": dict(sorted(counts.items())), "attention": problems}

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--directory", action="append", help="Read-only directory to scan; repeatable")
    ap.add_argument("--json", action="store_true", help="Machine-readable; review before sharing")
    args = ap.parse_args(argv)
    dirs = args.directory or [*DEFAULT_DIRS, str(Path.home() / ".local/share/applications")]
    report = summarize(scan(dirs))
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f'Launchers: {report["total"]}; need attention: {report["attention_count"]}')
        for status, count in report["status_counts"].items():
            print(f"  {status}: {count}")
        for row in report["attention"]:
            print(f'CHECK {row["status"]:20} {row["file"]}')
        print("Read-only inventory. 'CHECK' is not proof an application is broken.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
