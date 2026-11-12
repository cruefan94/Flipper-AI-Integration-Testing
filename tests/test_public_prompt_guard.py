import unittest
from scripts.public_prompt_guard import check_public_prompt

class PublicPromptGuardTests(unittest.TestCase):
    def test_normal_build_question_allowed(self):
        self.assertEqual(check_public_prompt("How do I fix an AI1 BLE timeout?"), "How do I fix an AI1 BLE timeout?")

    def test_secret_assignment_rejected(self):
        for prompt in ("api_key=abc123", "password: hello", "access token=abc123", "secret: xyz"):
            with self.subTest(prompt=prompt), self.assertRaises(ValueError):
                check_public_prompt(prompt)

    def test_github_token_rejected(self):
        with self.assertRaises(ValueError):
            check_public_prompt("token ghp_" + "a" * 40)

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            check_public_prompt(" ")

if __name__ == "__main__":
    unittest.main()
