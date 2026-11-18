"""Read-only Pironman systemd unit lint; never changes services or hardware."""
import argparse
import json
from pathlib import Path

def inspect_unit(text):
    findings = []
    section = None
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith(('#', ';')):
            continue
        if line.startswith('[') and line.endswith(']'):
            section = line[1:-1]
            continue
        if '=' not in line:
            findings.append({'line': number, 'code': 'invalid_assignment'})
            continue
        key, value = (x.strip() for x in line.split('=', 1))
        if section == 'Unit' and key in ('After', 'Before', 'Wants', 'Requires') and (' #' in value or ' ;' in value):
            findings.append({'line': number, 'code': 'inline_comment_in_dependency', 'detail': 'Move the comment onto its own line; systemd can parse comment words as dependencies'})
    return findings

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('unit', type=Path, help='Existing unit file to read')
    args = parser.parse_args()
    print(json.dumps({'path': str(args.unit), 'findings': inspect_unit(args.unit.read_text(encoding='utf-8'))}, indent=2))

if __name__ == '__main__':
    main()
