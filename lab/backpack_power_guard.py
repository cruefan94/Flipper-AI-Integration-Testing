"""Offline, fail-closed power-domain review for portable Flipper/ESP32 backpacks.

This does not measure current, infer board regulator limits, or operate hardware.
"""
from math import isfinite

ALLOWED = {'flipper_zero', 'esp32_wroom', 'esp32_s2', 'arduino_uno', 'sensor'}


def review(plan):
    errors = []
    if not isinstance(plan, dict):
        return ['plan must be an object']
    modules = plan.get('modules')
    if not isinstance(modules, list) or not modules:
        return ['nonempty modules list required']
    seen = set()
    for index, item in enumerate(modules):
        prefix = f'modules[{index}]'
        if not isinstance(item, dict):
            errors.append(f'{prefix}: object required')
            continue
        name = item.get('id')
        if not isinstance(name, str) or not name.strip() or name in seen:
            errors.append(f'{prefix}: unique nonempty id required')
        else:
            seen.add(name)
        if item.get('type') not in ALLOWED:
            errors.append(f'{prefix}: unsupported type')
        for field in ('supply_v', 'logic_v', 'peak_ma'):
            value = item.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value <= 0:
                errors.append(f'{prefix}: finite positive {field} required')
        if item.get('ground_verified') is not True:
            errors.append(f'{prefix}: common ground unverified')
        if item.get('supply_source') not in ('isolated_usb', 'verified_regulator'):
            errors.append(f'{prefix}: approved independent supply required')
        if item.get('type') in ('esp32_wroom', 'esp32_s2') and item.get('logic_v') != 3.3:
            errors.append(f'{prefix}: ESP32 logic must be 3.3V')
    if plan.get('gpio_direct_5v_to_3v3') is not False:
        errors.append('direct 5V-to-3.3V GPIO connection prohibited')
    if plan.get('backfeed_prevented') is not True:
        errors.append('backfeed isolation not verified')
    if plan.get('power_budget_verified') is not True:
        errors.append('supply current budget not verified externally')
    return errors


if __name__ == '__main__':
    import unittest

    def valid():
        return {'modules': [{'id': 'esp', 'type': 'esp32_wroom', 'supply_v': 5.0,
                             'logic_v': 3.3, 'peak_ma': 500, 'ground_verified': True,
                             'supply_source': 'isolated_usb'}],
                'gpio_direct_5v_to_3v3': False, 'backfeed_prevented': True,
                'power_budget_verified': True}

    class GuardTests(unittest.TestCase):
        def test_valid(self): self.assertEqual(review(valid()), [])
        def test_nan(self):
            p = valid(); p['modules'][0]['peak_ma'] = float('nan')
            self.assertTrue(review(p))
        def test_inf(self):
            p = valid(); p['modules'][0]['supply_v'] = float('inf')
            self.assertTrue(review(p))
        def test_5v_logic(self):
            p = valid(); p['modules'][0]['logic_v'] = 5
            self.assertTrue(review(p))
        def test_backfeed(self):
            p = valid(); p['backfeed_prevented'] = False
            self.assertTrue(review(p))
        def test_ground(self):
            p = valid(); p['modules'][0]['ground_verified'] = False
            self.assertTrue(review(p))
        def test_duplicate(self):
            p = valid(); p['modules'].append(dict(p['modules'][0]))
            self.assertTrue(review(p))
        def test_bool_voltage(self):
            p = valid(); p['modules'][0]['logic_v'] = True
            self.assertTrue(review(p))
        def test_budget(self):
            p = valid(); p['power_budget_verified'] = False
            self.assertTrue(review(p))
        def test_direct_5v(self):
            p = valid(); p['gpio_direct_5v_to_3v3'] = True
            self.assertTrue(review(p))

    unittest.main()
