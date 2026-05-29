from __future__ import annotations

from issuesense.console_diagnostics import analyze_console_log
from issuesense.engiagent import build_investigation_draft
from issuesense.explain import build_explanation
from issuesense.preprocessing import tokenize
from issuesense.predict import predict_baseline, predict_textcnn
from issuesense.qaforge import generate_test_plan
from issuesense.triage import build_triage_details


def run_suite_workflow(
    issue_text: str,
    requirement: str | None = None,
    model: str = "textcnn",
    input_type: str = "issue",
) -> dict:
    diagnostics = analyze_console_log(issue_text) if input_type == "console_log" else None
    normalized_issue = diagnostics["issue_text"] if diagnostics else issue_text
    prediction = _predict_with_triage(normalized_issue, model)
    triage_payload = {**prediction["triage"], "predicted_label": prediction["label"]}
    investigation = build_investigation_draft(normalized_issue, triage_payload)
    qa_requirement = requirement or _derive_requirement(normalized_issue, prediction)
    qa_plan = generate_test_plan(qa_requirement, triage_payload)
    readiness = _readiness_score(prediction, investigation, qa_plan)

    return {
        "suite": "Engineering Intelligence Suite",
        "status": "resolution_package_generated",
        "system_function": "Convert an engineering issue or test-report finding into a triage, investigation, and QA validation package.",
        "input": {
            "issue_text": issue_text,
            "normalized_issue_text": normalized_issue,
            "input_type": input_type,
            "requirement": qa_requirement,
            "model": model,
        },
        "console_diagnostics": diagnostics,
        "workflow_trace": [
            *(
                [
                    {
                        "module": "Console Diagnostics",
                        "action": "parsed console log into structured engineering issue context",
                        "output": diagnostics["primary_signal"]["id"],
                    }
                ]
                if diagnostics
                else []
            ),
            {
                "module": "IssueSense ML",
                "action": "classified issue, estimated likely cause, retrieved similar evidence",
                "output": prediction["label"],
            },
            {
                "module": "EngiAgent",
                "action": "orchestrated evidence through investigation workflow and generated 8D draft",
                "output": investigation["agent_runtime"],
            },
            {
                "module": "QAForge AI",
                "action": "generated requirement-linked tests and QA quality checks",
                "output": f"{qa_plan['coverage']['test_case_count']} test cases",
            },
        ],
        "resolution_package": {
            "triage": prediction,
            "investigation": investigation,
            "qa_plan": qa_plan,
        },
        "readiness": readiness,
        "recommended_next_action": _next_action(prediction, readiness),
    }


def _predict_with_triage(text: str, model: str) -> dict:
    prediction = predict_baseline(text) if model == "baseline" else predict_textcnn(text)
    explanation = build_explanation(text, prediction["label"], prediction["confidence"])
    token_count = len(tokenize(text))
    evidence_matches = sum(1 for example in explanation["similar_examples"] if example["label"] == prediction["label"])
    status = "needs_review" if token_count < 6 or prediction["confidence"] < 0.55 or evidence_matches == 0 else "auto_classified"
    prediction["status"] = status
    prediction["review_reasons"] = _review_reasons(prediction["confidence"], token_count, evidence_matches)
    prediction["input_quality"] = {
        "token_count": token_count,
        "matching_evidence_count": evidence_matches,
    }
    prediction["explanation"] = explanation
    prediction["triage"] = build_triage_details(text, prediction["label"], prediction["confidence"], status, evidence_matches)
    return prediction


def _derive_requirement(issue_text: str, prediction: dict) -> str:
    label = prediction["label"].replace("_", " ")
    cause = prediction["triage"]["likely_cause"]
    return (
        f"The system must handle the reported {label} scenario without recurrence. "
        f"Risk context: {issue_text} "
        f"Likely cause: {cause}. "
        "Validate expected behavior, invalid input, edge cases, regression impact, and integration impact."
    )


def _readiness_score(prediction: dict, investigation: dict, qa_plan: dict) -> dict:
    confidence_points = min(prediction["confidence"], 1.0) * 35
    evidence_points = min(prediction["input_quality"]["matching_evidence_count"], 3) / 3 * 20
    investigation_points = 25 if investigation.get("guardrails", {}).get("complete_8d_fields", True) else 10
    qa_points = min(qa_plan["coverage"]["coverage_percent"], 100) / 100 * 20
    score = round(confidence_points + evidence_points + investigation_points + qa_points, 1)
    return {
        "score": score,
        "level": "review_ready" if score >= 80 and prediction["status"] == "auto_classified" else "needs_human_review",
        "components": {
            "model_confidence_points": round(confidence_points, 1),
            "evidence_points": round(evidence_points, 1),
            "investigation_points": investigation_points,
            "qa_coverage_points": round(qa_points, 1),
        },
    }


def _next_action(prediction: dict, readiness: dict) -> str:
    if prediction["status"] == "needs_review":
        return "Ask an engineer to review the classification before using the 8D draft or QA plan."
    if readiness["level"] == "review_ready":
        return "Review the generated investigation and QA plan with engineering/QA owners, then convert accepted items into tracked work."
    return "Improve issue detail or add reviewed examples before relying on the generated package."


def _review_reasons(confidence: float, token_count: int, evidence_matches: int) -> list[str]:
    reasons = []
    if token_count < 6:
        reasons.append("Input is too short for reliable suite-level routing.")
    if confidence < 0.55:
        reasons.append("Model confidence is below the auto-routing threshold.")
    if evidence_matches == 0:
        reasons.append("Retrieved similar examples do not match the predicted label.")
    return reasons
