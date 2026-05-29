from __future__ import annotations

import re
import time


CONSOLE_PATTERNS = [
    {
        "id": "cors_blocked_request",
        "label": "integration_issue",
        "severity": "high",
        "patterns": ["cors", "access-control-allow-origin", "blocked by cors"],
        "cause": "CORS policy or cross-origin API configuration mismatch",
        "action": "Check API origin allowlist, credentials mode, preflight response, and gateway headers.",
    },
    {
        "id": "http_server_error",
        "label": "software_bug",
        "severity": "high",
        "patterns": [" 500 ", "status 500", "internal server error", "http_status"],
        "cause": "server-side exception or unhandled backend failure",
        "action": "Inspect backend logs for the failing request id, payload, stack trace, and error handler path.",
    },
    {
        "id": "http_not_found",
        "label": "integration_issue",
        "severity": "medium",
        "patterns": [" 404 ", "status 404", "not found"],
        "cause": "missing route, wrong base URL, or stale frontend API contract",
        "action": "Verify route registration, API base URL, proxy config, and frontend endpoint path.",
    },
    {
        "id": "javascript_type_error",
        "label": "software_bug",
        "severity": "high",
        "patterns": ["typeerror", "cannot read properties", "undefined is not", "is not a function"],
        "cause": "frontend state, null/undefined access, or invalid object contract",
        "action": "Trace the component props/state at the failing stack frame and add null-safe handling or schema validation.",
    },
    {
        "id": "unhandled_promise",
        "label": "software_bug",
        "severity": "medium",
        "patterns": ["unhandled promise", "uncaught (in promise)", "promise rejection"],
        "cause": "async error path missing catch or failed API response handling",
        "action": "Add explicit error handling around async calls and surface controlled UI/API failure states.",
    },
    {
        "id": "module_import_failure",
        "label": "test_environment_issue",
        "severity": "medium",
        "patterns": ["failed to resolve import", "module not found", "cannot find module", "failed to fetch dynamically imported module"],
        "cause": "dependency, build artifact, or module resolution problem",
        "action": "Check installed packages, import path casing, build output, Vite aliases, and deployment asset paths.",
    },
    {
        "id": "react_render_error",
        "label": "software_bug",
        "severity": "medium",
        "patterns": ["react", "error boundary", "hydration", "rendered fewer hooks", "invalid hook call"],
        "cause": "React render lifecycle, hook order, or hydration mismatch",
        "action": "Inspect component lifecycle, hook order, server/client markup, and error boundary output.",
    },
]


SIMULATED_CONSOLE_SCENARIOS = [
    {
        "id": "SIM-CORS-001",
        "expected_signal": "cors_blocked_request",
        "console_text": (
            "Access to fetch at 'http://127.0.0.1:8765/suite/run' from origin "
            "'http://127.0.0.1:5176' has been blocked by CORS policy: "
            "No 'Access-Control-Allow-Origin' header is present on the requested resource.\n"
            "Uncaught (in promise) TypeError: Failed to fetch\n"
            "    at runSuite (App.jsx:210:22)"
        ),
    },
    {
        "id": "SIM-500-001",
        "expected_signal": "http_server_error",
        "console_text": (
            "POST http://127.0.0.1:8765/predict 500 Internal Server Error\n"
            "Uncaught (in promise) Error: request failed with status 500\n"
            "    at classifyIssue (TriageConsole.jsx:88:19)"
        ),
    },
    {
        "id": "SIM-404-001",
        "expected_signal": "http_not_found",
        "console_text": (
            "GET http://127.0.0.1:8765/api/projects/active 404 Not Found\n"
            "Failed to load resource: the server responded with a status 404\n"
            "    at fetchProject (ProjectSelector.tsx:42:11)"
        ),
    },
    {
        "id": "SIM-TYPE-001",
        "expected_signal": "javascript_type_error",
        "console_text": (
            "Uncaught TypeError: Cannot read properties of undefined (reading 'map')\n"
            "    at ResultsPanel (ResultsPanel.jsx:51:28)\n"
            "    at renderWithHooks (react-dom_client.js:5521:18)"
        ),
    },
    {
        "id": "SIM-IMPORT-001",
        "expected_signal": "module_import_failure",
        "console_text": (
            "[vite] Failed to resolve import './components/MissingPanel.jsx' from 'src/App.jsx'. "
            "Does the file exist?\n"
            "    at TransformPluginContext.error (vite.js:32910:14)"
        ),
    },
    {
        "id": "SIM-REACT-001",
        "expected_signal": "react_render_error",
        "console_text": (
            "Warning: React has detected a change in the order of Hooks called by Dashboard.\n"
            "Error: Rendered fewer hooks than expected.\n"
            "    at Dashboard (Dashboard.jsx:77:5)"
        ),
    },
]


def analyze_console_log(console_text: str) -> dict:
    normalized = f" {console_text.lower()} "
    matches = []
    for rule in CONSOLE_PATTERNS:
        matched_terms = [term for term in rule["patterns"] if term in normalized]
        if matched_terms:
            matches.append(
                {
                    "id": rule["id"],
                    "predicted_label": rule["label"],
                    "severity": rule["severity"],
                    "likely_cause": rule["cause"],
                    "recommended_action": rule["action"],
                    "matched_terms": matched_terms,
                }
            )

    stack_frames = _extract_stack_frames(console_text)
    failing_urls = _extract_urls(console_text)
    primary = matches[0] if matches else _fallback(console_text)
    issue_text = _build_issue_text(console_text, primary, stack_frames, failing_urls)

    return {
        "module": "Console Diagnostics",
        "status": "diagnosed",
        "primary_signal": primary,
        "signals": matches,
        "stack_frames": stack_frames,
        "failing_urls": failing_urls,
        "issue_text": issue_text,
        "next_steps": _next_steps(primary, stack_frames, failing_urls),
    }


def run_console_self_test() -> dict:
    started = time.perf_counter()
    results = []
    for scenario in SIMULATED_CONSOLE_SCENARIOS:
        scenario_start = time.perf_counter()
        diagnostics = analyze_console_log(scenario["console_text"])
        detected = diagnostics["primary_signal"]["id"]
        passed = detected == scenario["expected_signal"]
        results.append(
            {
                "id": scenario["id"],
                "expected_signal": scenario["expected_signal"],
                "detected_signal": detected,
                "passed": passed,
                "severity": diagnostics["primary_signal"]["severity"],
                "likely_cause": diagnostics["primary_signal"]["likely_cause"],
                "latency_ms": round((time.perf_counter() - scenario_start) * 1000, 3),
            }
        )
    passed_count = sum(1 for result in results if result["passed"])
    return {
        "suite": "Console Diagnostics Self-Test",
        "scenario_count": len(results),
        "passed": passed_count,
        "failed": len(results) - passed_count,
        "detection_accuracy": round(passed_count / max(len(results), 1), 3),
        "latency_ms": round((time.perf_counter() - started) * 1000, 3),
        "results": results,
    }


def _extract_stack_frames(console_text: str) -> list[str]:
    frames = []
    for line in console_text.splitlines():
        stripped = line.strip()
        if re.search(r"\bat\b\s+.+:\d+:\d+", stripped) or re.search(r"\.(jsx?|tsx?):\d+:\d+", stripped):
            frames.append(stripped)
    return frames[:6]


def _extract_urls(console_text: str) -> list[str]:
    return re.findall(r"https?://[^\s)]+|/(?:api|assets|src)/[^\s)]+", console_text)[:6]


def _fallback(console_text: str) -> dict:
    severity = "high" if any(term in console_text.lower() for term in ["error", "exception", "failed"]) else "medium"
    return {
        "id": "unknown_console_error",
        "predicted_label": "software_bug",
        "severity": severity,
        "likely_cause": "runtime error requiring stack trace and reproduction context",
        "recommended_action": "Capture the full console output, reproduction steps, network response, and source stack frame.",
        "matched_terms": [],
    }


def _build_issue_text(console_text: str, primary: dict, stack_frames: list[str], failing_urls: list[str]) -> str:
    excerpt = " ".join(console_text.split())[:700]
    stack_text = f" Stack frame: {stack_frames[0]}." if stack_frames else ""
    url_text = f" Failing URL: {failing_urls[0]}." if failing_urls else ""
    return (
        f"Console diagnostics detected {primary['id']} with severity {primary['severity']}. "
        f"Likely cause: {primary['likely_cause']}. "
        f"Console excerpt: {excerpt}.{stack_text}{url_text}"
    )


def _next_steps(primary: dict, stack_frames: list[str], failing_urls: list[str]) -> list[str]:
    steps = [primary["recommended_action"]]
    if stack_frames:
        steps.append("Open the first stack frame and inspect the component/function state at that line.")
    if failing_urls:
        steps.append("Check the network request, response status, payload, and API route for the failing URL.")
    steps.append("Run the generated issue through the suite workflow to create an investigation draft and QA plan.")
    return steps
