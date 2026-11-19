"""Classify pasted kernel EXT4/storage log lines. Offline, read-only, stdlib only.

Input is a user-supplied text file or stdin; no device inspection, shell,
privilege, filesystem repair, or network activity. Avoid publishing raw logs.
"""
import argparse
import json
import re
import sys

EXT4 = re.compile(r"EXT4-fs (?:warning|error) \(device ([a-zA-Z0-9_-]+)\)", re.I)
EXT4_ERROR = re.compile(r"EXT4-fs error \(device [a-zA-Z0-9_-]+\)", re.I)
IO = re.compile(r"(?:error -5|I/O error|Buffer I/O error|blk_update_request|critical medium error)", re.I)
METADATA = re.compile(r"(?:metadata checksum (?:invalid|failed|error|mismatch)|checksum (?:invalid|failed|error|mismatch)|EXT4-fs error.*(?:error -117|corrupt(?:ed|ion)? (?:inode|directory|extent|metadata)))", re.I)
DIRECTORY = re.compile(r"(?:dx_probe|htree_dirblock_to_tree|reading directory block)", re.I)
DISCONNECT = re.compile(r"(?:usb .*disconnect|uas_eh_abort_handler|reset (?:SuperSpeed|high-speed) USB device)", re.I)
THROTTLE = re.compile(r"throttled=0x([0-9a-f]+)", re.I)
NEGATED_IO = re.compile(r"\b(?:no|zero|0)\s+(?:buffer\s+)?I/O\s+errors?\b", re.I)
NEGATED_REMOUNT = re.compile(r"\b(?:not|never|no)\s+(?:remounting|remounted)\s+filesystem\s+read-only\b", re.I)
READ_ONLY = re.compile(r"(?:EXT4-fs.*(?:remounting filesystem read-only|remounted filesystem read-only)|Remounting filesystem read-only)", re.I)
MAX_BYTES = 1024 * 1024

def classify(data):
    devices = set()
    ext4_count = io_count = directory_count = usb_count = readonly_count = metadata_count = ext4_error_count = 0
    throttled = None  # Bitwise union of all observed flags; never discard earlier warnings.
    for line in data.splitlines():
        m = EXT4.search(line)
        if m:
            ext4_count += 1
            devices.add(m.group(1) or m.group(2))
        ext4_error_count += bool(EXT4_ERROR.search(line))
        io_count += bool(IO.search(NEGATED_IO.sub("", line)))
        directory_count += bool(DIRECTORY.search(line))
        metadata_count += bool(METADATA.search(line))
        usb_count += bool(DISCONNECT.search(line))
        readonly_count += bool(READ_ONLY.search(NEGATED_REMOUNT.sub("", line)))
        # A pasted diagnostic line may contain multiple sampled values.
        # Aggregate every sample so a later clear reading cannot erase history.
        for t in THROTTLE.finditer(line):
            flag = int(t.group(1), 16)
            throttled = flag if throttled is None else (throttled | flag)
    critical = bool(ext4_error_count or io_count or readonly_count or metadata_count or (ext4_count and directory_count))
    return {
        "severity": "CRITICAL_STORAGE_RISK" if critical else ("REVIEW" if ext4_count or usb_count or (throttled is not None and throttled != 0) else "NO_MATCH"),
        "ext4_warning_lines": ext4_count,
        "ext4_explicit_error_lines": ext4_error_count,
        "io_error_lines": io_count,
        "directory_error_lines": directory_count,
        "metadata_corruption_lines": metadata_count,
        "usb_event_lines": usb_count,
        "readonly_remount_lines": readonly_count,
        "devices": sorted(devices),
        "throttling_flag_nonzero": None if throttled is None else bool(throttled),
        "guidance": ("Stop disk-intensive tasks; prioritize independent backup/recovery; "
                     "do not fsck a mounted root filesystem or assume a drive is failing. "
                     "Inspect cable, power, storage and filesystem from a safe recovery environment."
                     if critical else "No definitive storage diagnosis from these lines; nonzero throttling flags require power/thermal review, not proof of current undervoltage; inspect full private logs."),
        "limitations": "Pattern matches are clues, not proof of physical drive failure; no device operations performed."
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("log", nargs="?", help="Saved text log; omit for stdin")
    args = p.parse_args()
    if args.log:
        with open(args.log, "rb") as f:
            raw = f.read(MAX_BYTES + 1)
    else:
        raw = sys.stdin.buffer.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        p.error("Log exceeds 1 MiB safety limit")
    print(json.dumps(classify(raw.decode("utf-8", errors="replace")), indent=2))

if __name__ == "__main__":
    main()
