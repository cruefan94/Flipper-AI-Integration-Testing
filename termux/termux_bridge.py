#!/usr/bin/env python3
"""Flipper AI command bridge: private GitHub Issues <-> Termux (opt-in)."""
import argparse
import json
import os
import platform
import re
import subprocess
import sys
import time
from pathlib import Path

QUEUE = "cruefan94/Flipper-AI-Momentum-"  # private issue queue
OWNER = "cruefan94"
DEVICE = os.environ.get("FLIPPER_TERMUX_DEVICE", "phone")
HOME = Path.home().resolve()
WORK = HOME / "flipper-ai-workspace"
STATE = HOME / ".local" / "state" / "flipper-termux-bridge"
REPOS = {"momentum": ("cruefan94/Flipper-AI-Momentum-", WORK / "momentum"),
         "android": ("cruefan94/Flipper-AI-Android-Satellite", WORK / "android"),
         "testing": ("cruefan94/Flipper-AI-Integration-Testing", WORK / "testing")}
OPS = {"diagnostics", "repo_status", "workflow_runs", "shell"}

def redact(message):
    value = str(message)
    for p in (r"github_pat_[A-Za-z0-9_]+", r"gh[pousr]_[A-Za-z0-9_]{16,}",
              r"(?i)(authorization:\s*bearer\s+)\S+",
              r"(?i)((?:API_KEY|DEVICE_TOKEN|GITHUB_TOKEN|GH_TOKEN)=)\S+"):
        value = re.sub(p, lambda m: (m.group(1) if m.lastindex else "") + "[REDACTED]", value)
    return value[:10000]

def gh(method, path, data=None):
    args = ["gh", "api", "-X", method, path]
    if data is not None:
        args += ["--input", "-"]
    proc = subprocess.run(args, input=json.dumps(data) if data is not None else None,
                          text=True, capture_output=True, timeout=40)
    if proc.returncode:
        raise RuntimeError("GitHub API failed: " + redact(proc.stderr)[:500])
    return json.loads(proc.stdout) if proc.stdout.strip() else {}

def save(path, data):
    STATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(STATE, 0o700)
    temp = Path(str(path) + "." + str(os.getpid()) + ".tmp")
    with os.fdopen(os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w") as out:
        json.dump(data, out, indent=2)
    os.replace(temp, path)

def claim(path):
    try:
        os.close(os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600))
        return True
    except FileExistsError:
        return False

def paths(number):
    root = STATE / str(int(number))
    return [Path(str(root) + suffix) for suffix in (
        ".claimed", ".pending.json", ".result.json", ".commented", ".reported")]

def capture(argv, cwd=None, timeout=35):
    try:
        p = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return {"exit_code": p.returncode,
                "output": redact(p.stdout + ("\nSTDERR:\n" + p.stderr if p.stderr else ""))}
    except subprocess.TimeoutExpired:
        return {"exit_code": 124, "output": "Command timed out"}
    except Exception as exc:
        return {"exit_code": 1, "output": redact(exc)}

def execute(task):
    op, args = task["operation"], task["args"]
    if op == "diagnostics":
        info = {"device": DEVICE, "platform": platform.platform(), "python": sys.version.split()[0],
                "home": str(HOME), "workspace": str(WORK),
                "git": capture(["git", "--version"])["output"].strip(),
                "gh": capture(["gh", "--version"])["output"].splitlines()[:1],
                "clones": {name: folder.is_dir() for name, (_, folder) in REPOS.items()}}
        return {"exit_code": 0, "output": json.dumps(info, indent=2)}
    alias = args.get("repo", "momentum")
    if alias not in REPOS:
        return {"exit_code": 2, "output": "Unknown repository alias"}
    full_repo, folder = REPOS[alias]
    if op == "repo_status":
        if not (folder / ".git").exists():
            return {"exit_code": 2, "output": str(folder) + " has not been cloned"}
        return capture(["git", "-C", str(folder), "status", "--short", "--branch"])
    if op == "workflow_runs":
        data = gh("GET", f"repos/{full_repo}/actions/runs?per_page=5")
        runs = [{"id": x.get("id"), "name": x.get("name"), "status": x.get("status"),
                 "conclusion": x.get("conclusion"), "url": x.get("html_url")}
                for x in data.get("workflow_runs", [])]
        return {"exit_code": 0, "output": json.dumps(runs, indent=2)}
    if op == "shell":
        cmd, location = args.get("command"), args.get("cwd", "home")
        dirs = {"home": HOME, "workspace": WORK}
        dirs.update({a: folder for a, (_, folder) in REPOS.items()})
        if not isinstance(cmd, str) or not (1 <= len(cmd) <= 2000):
            return {"exit_code": 2, "output": "Invalid command"}
        if location not in dirs or not dirs[location].is_dir():
            return {"exit_code": 2, "output": "Unrecognized or missing working directory"}
        return capture(["bash", "-lc", cmd], str(dirs[location]), timeout=180)
    return {"exit_code": 2, "output": "Unsupported action"}

def parse_issue(issue):
    if issue.get("pull_request") or not issue.get("title", "").startswith("[Termux] "):
        return None
    if issue.get("user", {}).get("login", "").lower() != OWNER:
        return None
    try:
        task = json.loads(issue.get("body") or "")
    except (TypeError, ValueError):
        return None
    if not isinstance(task, dict) or task.get("schema") != 1 or task.get("device") != DEVICE:
        return None
    if task.get("operation") not in OPS or not isinstance(task.get("args"), dict):
        return None
    return task

def report_results():
    if not STATE.is_dir():
        return
    for file in sorted(STATE.glob("*.result.json")):
        number = int(file.name.split(".")[0])
        _, _, _, commented, reported = paths(number)
        if reported.exists():
            continue
        data = json.loads(file.read_text())
        output = redact(data["result"].get("output", "")).replace("~~~", "---")
        comment = ("Termux bridge result (device: " + DEVICE + "; operation: " +
                   data["operation"] + "; exit code: " + str(data["result"]["exit_code"]) +
                   ")\n\n~~~text\n" + output + "\n~~~")
        try:
            if not commented.exists():
                gh("POST", f"repos/{QUEUE}/issues/{number}/comments", {"body": comment})
                claim(commented)
            gh("PATCH", f"repos/{QUEUE}/issues/{number}", {"state": "closed"})
            claim(reported)
            print("Reported and closed #" + str(number), flush=True)
        except Exception as exc:
            print("Report retry pending #" + str(number) + ": " + redact(exc), flush=True)

def poll():
    STATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    report_results()
    for page in range(1, 11):
        issues = gh("GET", f"repos/{QUEUE}/issues?state=open&per_page=100&page={page}")
        for issue in issues:
            task = parse_issue(issue)
            if task is None:
                continue
            number = int(issue["number"])
            claimed, pending, result, _, _ = paths(number)
            if claimed.exists() or result.exists() or not claim(claimed):
                continue
            if task["operation"] == "shell":
                save(pending, task)
                print(f"Shell request #{number} pending: python termux_bridge.py approve {number}",
                      flush=True)
            else:
                try:
                    answer = execute(task)
                except Exception as exc:
                    answer = {"exit_code": 1, "output": redact(exc)}
                save(result, {"operation": task["operation"], "result": answer})
                print(f"Executed request #{number}: {task['operation']}", flush=True)
        if len(issues) < 100:
            break
    report_results()

def approve(number):
    _, pending, result, _, _ = paths(number)
    if not pending.exists() or result.exists():
        raise SystemExit("There is no unexecuted local-approval request for this number.")
    task = json.loads(pending.read_text())
    print(f"GitHub issue #{number}\nDirectory: {task['args'].get('cwd', 'home')}"
          f"\nCommand:\n{task['args'].get('command', '')}\n")
    if input("Type YES to run this exact command locally: ") != "YES":
        raise SystemExit("Not approved.")
    try:
        answer = execute(task)
    except Exception as exc:
        answer = {"exit_code": 1, "output": redact(exc)}
    save(result, {"operation": "shell", "result": answer})
    report_results()

def main():
    parser = argparse.ArgumentParser(description="Flipper AI / Termux private command bridge")
    sub = parser.add_subparsers(dest="mode", required=True)
    sub.add_parser("once")
    sub.add_parser("status")
    watch = sub.add_parser("watch")
    watch.add_argument("--interval", type=int, default=30)
    approve_parser = sub.add_parser("approve")
    approve_parser.add_argument("number", type=int)
    args = parser.parse_args()
    if args.mode == "status":
        print(json.dumps({"device": DEVICE, "queue": QUEUE, "state": str(STATE),
                          "pending": [p.name for p in STATE.glob("*.pending.json")
                                      if not Path(str(p).replace(".pending.json", ".result.json")).exists()]
                          if STATE.exists() else []}, indent=2))
    elif args.mode == "approve":
        approve(args.number)
    elif args.mode == "once":
        poll()
    else:
        seconds = max(15, args.interval)
        print(f"Monitoring {QUEUE} for device {DEVICE} every {seconds}s; Ctrl+C stops.",
              flush=True)
        while True:
            try:
                poll()
            except KeyboardInterrupt:
                return
            except Exception as exc:
                print("Polling error: " + redact(exc), flush=True)
            time.sleep(seconds)

if __name__ == "__main__":
    main()
