import unittest

from issuesense.preprocessing import normalize_text, tokenize


class PreprocessingTests(unittest.TestCase):
    def test_normalize_preserves_engineering_signals(self):
        text = "Login API returns 500 after 4.8s with 92% CPU."
        normalized = normalize_text(text)

        self.assertIn("http_status", normalized)
        self.assertIn("duration", normalized)
        self.assertIn("measure", normalized)
        self.assertIn("login api returns", normalized)

    def test_tokenize_removes_extra_whitespace(self):
        self.assertEqual(tokenize("  API   contract   changed  "), ["api", "contract", "changed"])


if __name__ == "__main__":
    unittest.main()
