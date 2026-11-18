import unittest
from pironman_service_lint import inspect_unit

class TestPironmanServiceLint(unittest.TestCase):
    def test_reported_invalid_inline_comment(self):
        result = inspect_unit('[Unit]\nAfter=multi-user.target # Need to start last\n')
        self.assertEqual(result[0]['code'], 'inline_comment_in_dependency')
        self.assertEqual(result[0]['line'], 2)

    def test_separate_comment_is_valid(self):
        self.assertEqual(inspect_unit('[Unit]\n# explanation\nAfter=multi-user.target\n'), [])

    def test_non_dependency_ignored(self):
        self.assertEqual(inspect_unit('[Service]\nExecStart=/bin/echo hello # literal\n'), [])

    def test_invalid_assignment(self):
        self.assertEqual(inspect_unit('[Unit]\nbadline\n')[0]['code'], 'invalid_assignment')

if __name__ == '__main__':
    unittest.main()
