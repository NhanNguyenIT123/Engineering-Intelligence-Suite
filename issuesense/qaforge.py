from __future__ import annotations

import re


QUALITY_RULES = [
    ("missing_expected_result", "Every generated case includes an explicit expected result."),
    ("duplicate_case", "Generated cases use distinct intents and test types."),
    ("weak_assertion", "Assertions name observable behavior instead of vague success criteria."),
    ("coverage_gap", "Traceability rows connect the requirement to functional, negative, edge, and regression checks."),
]


def generate_test_plan(requirement: str, triage: dict | None = None) -> dict:
    label = (triage or {}).get("predicted_label") or (triage or {}).get("label") or "software_bug"
    title = _requirement_title(requirement)
    cases = _base_cases(title, requirement, label)
    traceability = _traceability(requirement, cases)
    quality_checks = _quality_checks(cases, traceability)
    coverage = _coverage(cases, traceability)

    return {
        "module": "QAForge AI",
        "status": "test_plan_generated",
        "requirement_summary": title,
        "generated_cases": cases,
        "traceability": traceability,
        "coverage": coverage,
        "quality_checks": quality_checks,
        "export_targets": ["markdown", "csv", "test-management-import"],
    }


def _base_cases(title: str, requirement: str, label: str) -> list[dict]:
    cases = [
        {
            "id": "QA-001",
            "type": "functional",
            "title": f"Validate expected behavior for {title}",
            "steps": [
                "Prepare valid preconditions and test data.",
                "Execute the workflow described by the requirement.",
                "Observe API response, UI state, logs, and stored data.",
            ],
            "expected_result": "The system follows the stated expected behavior without unexpected error, state drift, or data corruption.",
        },
        {
            "id": "QA-002",
            "type": "negative",
            "title": f"Reject invalid or unsupported input for {title}",
            "steps": [
                "Prepare invalid, malformed, missing, or boundary input.",
                "Execute the same workflow.",
                "Inspect validation response and error handling.",
            ],
            "expected_result": "The system rejects the invalid condition with a controlled message/status and no unintended side effects.",
        },
        {
            "id": "QA-003",
            "type": "edge",
            "title": f"Exercise boundary conditions around {title}",
            "steps": [
                "Identify minimum, maximum, empty, duplicate, and special-character values.",
                "Run the workflow for each boundary condition.",
                "Compare results with acceptance criteria.",
            ],
            "expected_result": "Boundary cases produce deterministic and documented outcomes.",
        },
        {
            "id": "QA-004",
            "type": "regression",
            "title": f"Prevent recurrence of the reported issue in {title}",
            "steps": [
                "Reproduce the original failing scenario.",
                "Apply the fixed or clarified behavior.",
                "Run adjacent scenarios that previously passed.",
            ],
            "expected_result": "The original failure no longer occurs and adjacent behavior remains unchanged.",
        },
    ]

    if label == "integration_issue" or any(term in requirement.lower() for term in ["api", "connector", "service", "webhook"]):
        cases.append(
            {
                "id": "QA-005",
                "type": "integration",
                "title": "Verify producer/consumer API contract compatibility",
                "steps": [
                    "Send representative payloads from the producer service.",
                    "Validate field names, types, status semantics, and auth context at the consumer.",
                    "Repeat with retry and duplicate-event scenarios.",
                ],
                "expected_result": "Both systems interpret the same contract and handle retries without duplicated or missed state.",
            }
        )
    if label == "performance_issue" or any(term in requirement.lower() for term in ["slow", "latency", "timeout", "100k", "performance"]):
        cases.append(
            {
                "id": "QA-006",
                "type": "performance",
                "title": "Measure behavior under representative load",
                "steps": [
                    "Prepare small, medium, and large datasets.",
                    "Execute the workflow while collecting latency and resource metrics.",
                    "Compare results against the agreed threshold.",
                ],
                "expected_result": "Latency and resource usage remain within the defined threshold for the target workload.",
            }
        )
    if label == "test_environment_issue" or any(term in requirement.lower() for term in ["staging", "config", "environment", "sandbox"]):
        cases.append(
            {
                "id": "QA-007",
                "type": "environment",
                "title": "Validate environment configuration assumptions",
                "steps": [
                    "Compare required variables, migrations, credentials, and dependencies across environments.",
                    "Run the same scenario in local, CI, and staging.",
                    "Record differences that affect the observed result.",
                ],
                "expected_result": "The behavior is consistent across environments or the documented environment difference explains the result.",
            }
        )

    return cases


def _traceability(requirement: str, cases: list[dict]) -> list[dict]:
    fragments = _requirement_fragments(requirement)
    rows = []
    for index, fragment in enumerate(fragments[:4], start=1):
        related = [case["id"] for case in cases if case["type"] in _types_for_fragment(fragment)]
        if not related:
            related = [cases[min(index - 1, len(cases) - 1)]["id"]]
        rows.append({"requirement_id": f"REQ-{index:02d}", "fragment": fragment, "test_ids": related})
    return rows


def _quality_checks(cases: list[dict], traceability: list[dict]) -> list[dict]:
    titles = [case["title"].lower() for case in cases]
    duplicates = len(titles) - len(set(titles))
    missing_expected = sum(1 for case in cases if not case.get("expected_result"))
    weak = sum(1 for case in cases if any(term in case["expected_result"].lower() for term in ["works", "ok", "success"]))
    gaps = sum(1 for row in traceability if not row["test_ids"])
    values = {
        "missing_expected_result": missing_expected,
        "duplicate_case": duplicates,
        "weak_assertion": weak,
        "coverage_gap": gaps,
    }
    return [
        {"id": rule_id, "status": "pass" if values[rule_id] == 0 else "review", "finding": text, "count": values[rule_id]}
        for rule_id, text in QUALITY_RULES
    ]


def _coverage(cases: list[dict], traceability: list[dict]) -> dict:
    covered_rows = sum(1 for row in traceability if row["test_ids"])
    categories = sorted({case["type"] for case in cases})
    return {
        "requirement_fragments": len(traceability),
        "covered_fragments": covered_rows,
        "coverage_percent": round((covered_rows / max(len(traceability), 1)) * 100, 1),
        "test_case_count": len(cases),
        "test_types": categories,
    }


def _requirement_title(requirement: str) -> str:
    clean = " ".join(requirement.split())
    first = re.split(r"(?<=[.!?])\s+", clean)[0]
    if len(first) > 110:
        first = f"{first[:107]}..."
    return first or "submitted requirement"


def _requirement_fragments(requirement: str) -> list[str]:
    pieces = [part.strip(" .") for part in re.split(r"[.;\n]", requirement) if part.strip()]
    return pieces or [_requirement_title(requirement)]


def _types_for_fragment(fragment: str) -> list[str]:
    lowered = fragment.lower()
    types = ["functional"]
    if any(term in lowered for term in ["invalid", "missing", "reject", "error", "fail"]):
        types.append("negative")
    if any(term in lowered for term in ["boundary", "special", "empty", "duplicate", "maximum", "minimum"]):
        types.append("edge")
    if any(term in lowered for term in ["api", "service", "connector", "webhook"]):
        types.append("integration")
    if any(term in lowered for term in ["slow", "latency", "timeout", "performance"]):
        types.append("performance")
    return types
