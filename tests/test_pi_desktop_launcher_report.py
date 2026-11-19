import unittest
from raspberry_pi.desktop_launcher_report import summarize

class LauncherReportTests(unittest.TestCase):
    def test_attention_and_counts(self):
        rows = [{"file": "a.desktop", "status": "executable_found"},
                {"file": "b.desktop", "status": "missing_tryexec"},
                {"file": "c.desktop", "status": "hidden"},
                {"file": "d.desktop", "status": "review_wrapper"}]
        result = summarize(rows)
        self.assertEqual(result["total"], 4)
        self.assertEqual(result["attention_count"], 2)
        self.assertEqual([r["file"] for r in result["attention"]], ["b.desktop", "d.desktop"])
        self.assertEqual(result["status_counts"]["hidden"], 1)

    def test_empty(self):
        self.assertEqual(summarize([]), {"total": 0, "attention_count": 0,
                                          "status_counts": {}, "attention": []})

    def test_duplicate_names_preserved(self):
        result = summarize([{"file": "app.desktop", "status": "missing_exec"},
                            {"file": "app.desktop", "status": "missing_exec"}])
        self.assertEqual(result["attention_count"], 2)

if __name__ == "__main__":
    unittest.main()
