import unittest

from issuesense.engiagent import build_investigation_draft
from issuesense.console_diagnostics import analyze_console_log
from issuesense.qaforge import generate_test_plan
from issuesense.suite import run_suite_workflow


class SuiteModuleTests(unittest.TestCase):
    def test_engiagent_builds_complete_8d_draft(self):
        result = build_investigation_draft(
            "The ERP connector sends customerId but the CRM endpoint expects customer_id.",
            {"predicted_label": "integration_issue", "likely_cause": "API field contract mismatch"},
        )

        self.assertEqual(result["module"], "EngiAgent")
        self.assertIn(result["agent_runtime"], {"langchain_core_runnable_chain", "deterministic_fallback"})
        self.assertEqual(len(result["eight_d"]), 8)
        self.assertIn("contract", result["eight_d"]["D6_validation_plan"].lower())
        self.assertGreaterEqual(len(result["tool_trace"]), 3)
        self.assertTrue(result.get("guardrails", {"complete_8d_fields": True})["complete_8d_fields"])

    def test_qaforge_generates_traceable_test_plan(self):
        result = generate_test_plan(
            "The CRM connector must map customerId to customer_id and reject malformed payloads.",
            {"predicted_label": "integration_issue"},
        )

        self.assertEqual(result["module"], "QAForge AI")
        self.assertGreaterEqual(len(result["generated_cases"]), 5)
        self.assertEqual(result["coverage"]["coverage_percent"], 100.0)
        self.assertTrue(all(check["status"] == "pass" for check in result["quality_checks"]))

    def test_suite_generates_resolution_package(self):
        result = run_suite_workflow(
            "The ERP connector sends customerId but the CRM endpoint now expects customer_id.",
        )

        self.assertEqual(result["suite"], "Engineering Intelligence Suite")
        self.assertEqual(result["status"], "resolution_package_generated")
        self.assertIn("triage", result["resolution_package"])
        self.assertIn("investigation", result["resolution_package"])
        self.assertIn("qa_plan", result["resolution_package"])
        self.assertGreaterEqual(len(result["workflow_trace"]), 3)

    def test_console_diagnostics_detects_cors_and_runs_suite(self):
        console = (
            "Access to fetch at 'http://127.0.0.1:8765/suite/run' from origin "
            "'http://127.0.0.1:5176' has been blocked by CORS policy. "
            "Uncaught (in promise) TypeError: Failed to fetch at runSuite (App.jsx:210:22)"
        )
        diagnostics = analyze_console_log(console)
        result = run_suite_workflow(console, input_type="console_log")

        self.assertEqual(diagnostics["primary_signal"]["id"], "cors_blocked_request")
        self.assertEqual(result["console_diagnostics"]["primary_signal"]["id"], "cors_blocked_request")
        self.assertGreaterEqual(len(result["workflow_trace"]), 4)


if __name__ == "__main__":
    unittest.main()
