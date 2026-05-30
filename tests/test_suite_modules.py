import unittest

from issuesense.engiagent import build_investigation_draft
from issuesense.console_diagnostics import analyze_console_log, run_console_self_test
from issuesense.document_ingestion import analyze_engineering_document, chunk_document_text
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

    def test_console_self_test_scenarios_pass(self):
        result = run_console_self_test()

        self.assertEqual(result["scenario_count"], 6)
        self.assertEqual(result["detection_accuracy"], 1.0)
        self.assertTrue(all(item["passed"] for item in result["results"]))

    def test_engiagent_analyzes_uploaded_text_document(self):
        report = (
            "Test Report: Checkout regression failure\n\n"
            "Expected: payment confirmation is returned within 2 seconds.\n"
            "Actual: staging returns HTTP 500 after 14 seconds when the sandbox provider is called.\n"
            "The failure is reproducible only on staging after the latest connector deployment."
        )

        result = analyze_engineering_document(
            "checkout-test-report.md",
            report.encode("utf-8"),
            {"predicted_label": "test_environment_issue", "likely_cause": "staging payment sandbox mismatch"},
        )

        self.assertEqual(result["module"], "EngiAgent")
        self.assertEqual(result["summary"]["document_type"], "test_report")
        self.assertGreaterEqual(result["document"]["chunk_count"], 1)
        self.assertGreaterEqual(len(result["evidence"]), 1)
        self.assertEqual(result["investigation"]["module"], "EngiAgent")
        self.assertIn("D4_root_cause_hypothesis", result["investigation"]["eight_d"])

    def test_document_chunker_preserves_signal_scores(self):
        chunks = chunk_document_text(
            "First paragraph has no risk.\n\nSecond paragraph reports timeout and API error in staging.",
            chunk_size=35,
        )

        self.assertEqual(len(chunks), 2)
        self.assertGreater(chunks[1]["signal_score"], chunks[0]["signal_score"])


if __name__ == "__main__":
    unittest.main()
