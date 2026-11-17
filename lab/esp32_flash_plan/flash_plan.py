"""Offline, fail-closed ESP32 flash-plan validator. Never opens ports or runs tools."""
import json
import re
import sys

CHIPS = {'esp32', 'esp32s2'}
PORT = re.compile(r'^/dev/serial/by-id/[A-Za-z0-9_.:+-]+$')
SHA = re.compile(r'^[0-9a-f]{64}$')


def validate(plan):
    if not isinstance(plan, dict):
        return ['plan must be an object']
    errors = []
    if plan.get('chip') not in CHIPS:
        errors.append('unsupported chip')
    if not isinstance(plan.get('port'), str) or not PORT.fullmatch(plan['port']):
        errors.append('stable by-id port required')
    if plan.get('observed_chip') != plan.get('chip'):
        errors.append('observed chip mismatch')
    if plan.get('operation') != 'review-only':
        errors.append('only review-only operation allowed')
    if plan.get('common_ground_verified') is not True:
        errors.append('common ground unverified')
    if type(plan.get('uart_voltage_v')) not in (float, int) or not 0 < plan['uart_voltage_v'] <= 3.3:
        errors.append('invalid UART voltage')
    if not isinstance(plan.get('image_sha256'), str) or not SHA.fullmatch(plan['image_sha256']):
        errors.append('invalid image digest')
    if plan.get('board_identity_verified') is not True:
        errors.append('board identity unverified')
    return errors


def main():
    try:
        data = json.load(sys.stdin)
        errors = validate(data)
    except (ValueError, TypeError) as exc:
        errors = ['invalid JSON: ' + type(exc).__name__]
    print(json.dumps({'safe_for_offline_review': not errors, 'errors': errors}, sort_keys=True))
    return 0 if not errors else 2


if __name__ == '__main__':
    raise SystemExit(main())
