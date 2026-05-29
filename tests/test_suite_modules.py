import unittest

from issuesense.engiagent import build_investigation_draft
from issuesense.qaforge import generate_test_plan


class SuiteModuleTests(unittest.TestCase):
    def test_engiagent_builds_complete_8d_draft(self):
        result = build_investigation_draft(
            "The ERP connector sends customerId but the CRM endpoint expects customer_id.",
            {"predicted_label": "integration_issue", "likely_cause": "API field contract mismatch"},
        )

        self.assertEqual(result["module"], "EngiAgent")
        self.assertEqual(len(result["eight_d"]), 8)
        self.assertIn("contract", result["eight_d"]["D6_validation_plan"].lower())
        self.assertGreaterEqual(len(result["tool_trace"]), 3)

    def test_qaforge_generates_traceable_test_plan(self):
        result = generate_test_plan(
            "The CRM connector must map customerId to customer_id and reject malformed payloads.",
            {"predicted_label": "integration_issue"},
        )

        self.assertEqual(result["module"], "QAForge AI")
        self.assertGreaterEqual(len(result["generated_cases"]), 5)
        self.assertEqual(result["coverage"]["coverage_percent"], 100.0)
        self.assertTrue(all(check["status"] == "pass" for check in result["quality_checks"]))


if __name__ == "__main__":
    unittest.main()
