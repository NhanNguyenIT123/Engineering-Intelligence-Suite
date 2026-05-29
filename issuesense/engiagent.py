from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class InvestigationProfile:
    likely_cause: str
    containment: str
    corrective_action: str
    validation: str
    prevention: str


PROFILES = {
    "software_bug": InvestigationProfile(
        likely_cause="application logic or error-handling defect",
        containment="Reproduce the failure with the smallest input and add temporary monitoring around the failing endpoint or workflow.",
        corrective_action="Patch the failing validation, state update, or exception handling path and keep the behavior aligned with the expected contract.",
        validation="Run the original failing case, adjacent edge cases, and a regression test covering the broken behavior.",
        prevention="Add automated regression coverage and log the failure mode in the engineering checklist.",
    ),
    "requirement_gap": InvestigationProfile(
        likely_cause="missing or ambiguous expected behavior",
        containment="Pause implementation decisions that depend on the unclear behavior and document the open product question.",
        corrective_action="Clarify acceptance criteria with the product or domain owner and convert the answer into explicit workflow rules.",
        validation="Review the clarified rule with QA and add positive, negative, and boundary tests.",
        prevention="Require acceptance criteria and edge-case notes before moving similar stories into implementation.",
    ),
    "test_environment_issue": InvestigationProfile(
        likely_cause="environment, configuration, or dependency mismatch",
        containment="Isolate the failing environment and compare it against local and CI configuration before blaming application code.",
        corrective_action="Fix the missing config, dependency, credential, migration, network route, or service availability problem.",
        validation="Re-run the same test in local, CI, and staging with the environment variables captured.",
        prevention="Version environment assumptions and add pre-flight checks for required dependencies.",
    ),
    "data_issue": InvestigationProfile(
        likely_cause="missing, malformed, duplicated, or inconsistent data",
        containment="Identify impacted records and block downstream reports or model consumption until data quality is verified.",
        corrective_action="Repair the source records or transformation step that created bad values, duplicates, or schema drift.",
        validation="Run data validation checks on nulls, duplicates, schema, formats, and affected aggregates.",
        prevention="Add data contracts and import validation before records are consumed by reports or services.",
    ),
    "performance_issue": InvestigationProfile(
        likely_cause="latency, throughput, memory, or scaling bottleneck",
        containment="Capture the slow path, workload size, resource usage, and timeout conditions before changing implementation.",
        corrective_action="Optimize the dominant bottleneck, such as query shape, batch size, caching, indexing, or rendering work.",
        validation="Benchmark small and large workloads and compare latency, CPU, memory, and timeout rate.",
        prevention="Add performance regression thresholds to the release or CI checklist.",
    ),
    "integration_issue": InvestigationProfile(
        likely_cause="API contract, authentication, webhook, or service synchronization mismatch",
        containment="Freeze the failing payload and compare producer/consumer contracts before applying a workaround.",
        corrective_action="Align field names, types, status semantics, auth settings, callback registration, or retry behavior across services.",
        validation="Run contract, integration, and idempotency tests across the connected systems.",
        prevention="Maintain API contract tests and change-notification notes for integration owners.",
    ),
}


def build_investigation_draft(text: str, triage: dict | None = None) -> dict:
    label = _extract_label(triage)
    profile = PROFILES.get(label, _fallback_profile(text))
    evidence = _extract_evidence(text)
    problem = _summarize_problem(text, triage)

    return {
        "module": "EngiAgent",
        "status": "draft_generated",
        "input_summary": problem,
        "investigation_summary": (
            f"The finding is treated as {label.replace('_', ' ')}. "
            f"The current hypothesis is {profile.likely_cause}. "
            f"The draft should be reviewed by engineering/QA before execution."
        ),
        "eight_d": {
            "D1_team": "Software engineer, QA engineer, product/domain owner, and integration or data owner if applicable.",
            "D2_problem_description": problem,
            "D3_containment_action": profile.containment,
            "D4_root_cause_hypothesis": triage.get("likely_cause", profile.likely_cause) if triage else profile.likely_cause,
            "D5_corrective_action": profile.corrective_action,
            "D6_validation_plan": profile.validation,
            "D7_prevention_plan": profile.prevention,
            "D8_closure_note": "Close after evidence, fix, validation result, and owner sign-off are documented.",
        },
        "evidence": evidence,
        "tool_trace": [
            {"tool": "issue_intake_parser", "result": f"{len(evidence)} evidence signal(s) extracted"},
            {"tool": "triage_context_reader", "result": f"label={label}"},
            {"tool": "8d_template_builder", "result": "D1-D8 draft generated from grounded triage context"},
        ],
        "memory_notes": [
            "This MVP stores no persistent user memory.",
            "The generated 8D is a structured draft, not a final root-cause conclusion.",
        ],
    }


def _extract_label(triage: dict | None) -> str:
    if not triage:
        return "software_bug"
    return triage.get("predicted_label") or triage.get("label") or triage.get("category") or "software_bug"


def _extract_evidence(text: str) -> list[dict]:
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]
    evidence = []
    for index, sentence in enumerate(sentences[:5], start=1):
        evidence.append({"id": f"EV-{index:02d}", "text": sentence, "source": "submitted_report"})
    if not evidence:
        evidence.append({"id": "EV-01", "text": text[:240], "source": "submitted_report"})
    return evidence


def _summarize_problem(text: str, triage: dict | None) -> str:
    clean = " ".join(text.split())
    if len(clean) > 280:
        clean = f"{clean[:277]}..."
    if triage and triage.get("likely_cause") and "likely cause from issuesense" not in clean.lower():
        return f"{clean} Likely cause from IssueSense: {triage['likely_cause']}."
    return clean


def _fallback_profile(text: str) -> InvestigationProfile:
    lowered = text.lower()
    if any(term in lowered for term in ["slow", "latency", "timeout", "memory", "cpu"]):
        return PROFILES["performance_issue"]
    if any(term in lowered for term in ["staging", "local", "config", "sandbox", "environment"]):
        return PROFILES["test_environment_issue"]
    if any(term in lowered for term in ["requirement", "expected", "acceptance", "unclear"]):
        return PROFILES["requirement_gap"]
    return PROFILES["software_bug"]
