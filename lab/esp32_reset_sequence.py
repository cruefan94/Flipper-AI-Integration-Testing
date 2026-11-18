"""Offline ESP32 reset/strap sequence validator. No GPIO or serial access."""
import json
import sys

VALID = {'wroom': {'boot': 0, 'en': 1}, 's2': {'boot': 0, 'en': 1}}

def validate(data):
    if not isinstance(data, dict) or data.get('chip') not in VALID:
        return {'ok': False, 'reason': 'unsupported chip'}
    events = data.get('events')
    if not isinstance(events, list) or len(events) > 32:
        return {'ok': False, 'reason': 'invalid event list'}
    boot = en = 1
    saw_reset_low = saw_release = False
    for event in events:
        if not isinstance(event, dict) or set(event) != {'pin', 'level'}:
            return {'ok': False, 'reason': 'invalid event'}
        pin, level = event['pin'], event['level']
        if pin not in ('BOOT', 'EN') or type(level) is not int or level not in (0, 1):
            return {'ok': False, 'reason': 'invalid pin or level'}
        if pin == 'BOOT':
            boot = level
        else:
            if level == 0:
                saw_reset_low = True
            if level == 1 and en == 0 and saw_reset_low and boot == 0:
                saw_release = True
            en = level
    if saw_release:
        return {'ok': True, 'reason': 'download-mode strap sequence observed; ROM confirmation still required'}
    return {'ok': False, 'reason': 'no EN rising edge while BOOT held low'}

if __name__ == '__main__':
    print(json.dumps(validate(json.load(sys.stdin)), sort_keys=True))
