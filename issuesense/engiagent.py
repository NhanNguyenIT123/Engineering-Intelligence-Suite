from __future__ import annotations

import os
import re
from dataclasses import dataclass

try:
    from langchain_core.runnables import RunnableLambda
    from langchain_core.tools import tool

    LANGCHAIN_CORE_AVAILABLE = True
except ImportError:
    RunnableLambda = None
    tool = None
    LANGCHAIN_CORE_AVAILABLE = False


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
    "document_review": InvestigationProfile(
        likely_cause="reference document or requirement context, not a confirmed engineering failure",
        containment="Do not open a defect from this document alone; extract requirements, assumptions, and open questions first.",
        corrective_action="Convert the document into explicit requirements, owners, risks, and follow-up questions before routing it into issue triage.",
        validation="Review extracted requirements and assumptions with the product or engineering owner.",
        prevention="Keep reference documents separated from confirmed incident reports in the intake workflow.",
    ),
}


if LANGCHAIN_CORE_AVAILABLE:

    @tool
    def parse_issue_evidence(text: str) -> list[dict]:
        """Extract evidence snippets from an engineering issue or test report."""
        return _extract_evidence(text)

    @tool
    def choose_investigation_profile(label: str, text: str) -> dict:
        """Choose the investigation profile that should drive the 8D workflow."""
        profile = PROFILES.get(label, _fallback_profile(text))
        return {
            "likely_cause": profile.likely_cause,
            "containment": profile.containment,
            "corrective_action": profile.corrective_action,
            "validation": profile.validation,
            "prevention": profile.prevention,
        }


def build_investigation_draft(text: str, triage: dict | None = None) -> dict:
    runtime = os.getenv("ENGIAGENT_RUNTIME", "langchain").lower()
    if runtime == "langchain" and LANGCHAIN_CORE_AVAILABLE:
        return _build_langchain_investigation(text, triage)
    return _build_deterministic_investigation(text, triage, fallback_reason=_fallback_reason(runtime))


def _build_langchain_investigation(text: str, triage: dict | None = None) -> dict:
    initial_state = {
        "text": text,
        "triage": triage or {},
        "agent_plan": [
            "Parse report evidence.",
            "Route the issue through triage context.",
            "Generate an 8D investigation draft.",
            "Run grounding and completeness guardrails.",
        ],
        "tool_trace": [],
    }
    chain = (
        RunnableLambda(_intake_parser_stage)
        | RunnableLambda(_triage_router_stage)
        | RunnableLambda(_eight_d_builder_stage)
        | RunnableLambda(_guardrail_stage)
    )
    result = chain.invoke(initial_state)
    result["agent_runtime"] = "langchain_core_runnable_chain"
    result["module"] = "EngiAgent"
    result["status"] = "draft_generated"
    result["registered_tools"] = [
        "parse_issue_evidence",
        "choose_investigation_profile",
        "issue_intake_parser",
        "triage_context_router",
        "eight_d_workflow_builder",
        "grounding_guardrail",
    ]
    return result


def _build_deterministic_investigation(
    text: str,
    triage: dict | None = None,
    fallback_reason: str = "langchain unavailable",
) -> dict:
    label = _extract_label(triage)
    profile = PROFILES.get(label, _fallback_profile(text))
    evidence = _extract_evidence(text)
    problem = _summarize_problem(text, triage)

    return {
        "module": "EngiAgent",
        "status": "draft_generated",
        "agent_runtime": "deterministic_fallback",
        "fallback_reason": fallback_reason,
        "agent_plan": [
            "Parse report evidence.",
            "Route the issue through triage context.",
            "Generate an 8D investigation draft.",
            "Run grounding and completeness guardrails.",
        ],
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
        "guardrails": {
            "grounded_in_submitted_report": len(evidence) > 0,
            "complete_8d_fields": True,
            "missing_fields": [],
            "requires_human_approval": True,
        },
    }


def _intake_parser_stage(state: dict) -> dict:
    evidence = parse_issue_evidence.invoke({"text": state["text"]})
    state["evidence"] = evidence
    state["tool_trace"].append(
        {
            "tool": "issue_intake_parser",
            "runtime": "langchain_core",
            "result": f"{len(evidence)} evidence signal(s) extracted",
        }
    )
    return state


def _triage_router_stage(state: dict) -> dict:
    label = _extract_label(state.get("triage"))
    profile_data = choose_investigation_profile.invoke({"label": label, "text": state["text"]})
    profile = InvestigationProfile(**profile_data)
    state["predicted_label"] = label
    state["profile"] = profile
    state["input_summary"] = _summarize_problem(state["text"], state.get("triage"))
    state["tool_trace"].append(
        {
            "tool": "triage_context_router",
            "runtime": "langchain_core",
            "result": f"label={label}; likely_cause={state.get('triage', {}).get('likely_cause', profile.likely_cause)}",
        }
    )
    return state


def _eight_d_builder_stage(state: dict) -> dict:
    profile = state["profile"]
    triage = state.get("triage") or {}
    label = state["predicted_label"]
    problem = state["input_summary"]
    if label == "document_review":
        state["investigation_summary"] = (
            "The upload is treated as reference or requirement context, not a confirmed defect. "
            "EngiAgent extracted review evidence and drafted next steps for human validation."
        )
    else:
        state["investigation_summary"] = (
            f"The finding is treated as {label.replace('_', ' ')}. "
            f"The agent routed evidence through the {label} workflow and drafted actions for human review."
        )
    state["eight_d"] = {
        "D1_team": "Software engineer, QA engineer, product/domain owner, and integration or data owner if applicable.",
        "D2_problem_description": problem,
        "D3_containment_action": profile.containment,
        "D4_root_cause_hypothesis": triage.get("likely_cause", profile.likely_cause),
        "D5_corrective_action": profile.corrective_action,
        "D6_validation_plan": profile.validation,
        "D7_prevention_plan": profile.prevention,
        "D8_closure_note": "Close after evidence, fix, validation result, and owner sign-off are documented.",
    }
    state["tool_trace"].append(
        {
            "tool": "eight_d_workflow_builder",
            "runtime": "langchain_core",
            "result": "D1-D8 draft generated from routed triage context",
        }
    )
    return state


def _guardrail_stage(state: dict) -> dict:
    eight_d = state["eight_d"]
    missing = [key for key, value in eight_d.items() if not value]
    state["guardrails"] = {
        "grounded_in_submitted_report": len(state.get("evidence", [])) > 0,
        "complete_8d_fields": len(missing) == 0,
        "missing_fields": missing,
        "requires_human_approval": True,
    }
    state["tool_trace"].append(
        {
            "tool": "grounding_guardrail",
            "runtime": "langchain_core",
            "result": "8D draft passed completeness check; human approval required",
        }
    )
    state["memory_notes"] = [
        "This local MVP keeps memory inside the request state only.",
        "Production memory would require session storage, audit logs, and access control.",
    ]
    state.pop("profile", None)
    state.pop("text", None)
    state.pop("triage", None)
    return state


def _extract_label(triage: dict | None) -> str:
    if not triage:
        return "document_review"
    return triage.get("predicted_label") or triage.get("label") or triage.get("category") or "document_review"


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


def _fallback_reason(runtime: str) -> str:
    if runtime != "langchain":
        return f"ENGIAGENT_RUNTIME={runtime}"
    return "langchain-core is not installed"
