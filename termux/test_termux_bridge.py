import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('termux_bridge', ROOT / 'termux_bridge.py')
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)

class BridgeContractTests(unittest.TestCase):
    def request(self, title='[Termux] Diagnostics', author='cruefan94', operation='diagnostics', args=None, device='phone'):
        return {'title': title, 'user': {'login': author}, 'body': json.dumps({
            'schema': 1, 'device': device, 'operation': operation, 'args': args or {}})}

    def test_accept_owner_private_request(self):
        self.assertEqual(bridge.parse_issue(self.request())['operation'], 'diagnostics')

    def test_reject_non_owner(self):
        self.assertIsNone(bridge.parse_issue(self.request(author='intruder')))

    def test_reject_other_device(self):
        self.assertIsNone(bridge.parse_issue(self.request(device='other-phone')))

    def test_reject_unknown_op(self):
        self.assertIsNone(bridge.parse_issue(self.request(operation='delete_phone')))

    def test_reject_pull_request(self):
        data = self.request()
        data['pull_request'] = {'url': 'https://example.invalid'}
        self.assertIsNone(bridge.parse_issue(data))

    def test_diagnostics_is_read_only(self):
        result = bridge.execute({'operation': 'diagnostics', 'args': {}})
        self.assertEqual(result['exit_code'], 0)
        info = json.loads(result['output'])
        self.assertIn('clones', info)

    def test_repo_alias_rejection(self):
        result = bridge.execute({'operation': 'repo_status', 'args': {'repo': 'unknown'}})
        self.assertEqual(result['exit_code'], 2)

    def test_shell_uses_explicit_directory_alias(self):
        result = bridge.execute({'operation': 'shell', 'args': {'command': 'pwd', 'cwd': '/tmp'}})
        self.assertEqual(result['exit_code'], 2)

    def test_local_approval_denial(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(bridge, 'STATE', Path(folder)):
            _, pending, result, _, _ = bridge.paths(123)
            pending.write_text(json.dumps({'schema': 1, 'device': 'phone',
                'operation': 'shell', 'args': {'command': 'pwd', 'cwd': 'home'}}))
            with patch('builtins.input', return_value='NO'):
                with self.assertRaises(SystemExit):
                    bridge.approve(123)
            self.assertFalse(result.exists())

if __name__ == '__main__':
    unittest.main()
