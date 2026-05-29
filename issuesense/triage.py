from issuesense.preprocessing import normalize_text


CAUSE_RULES = {
    "software_bug": {
        "default": "application behavior or error-handling defect",
        "signals": {
            "validation or input handling defect": ["special", "invalid", "validation", "malformed", "input"],
            "server-side exception handling defect": ["500", "http_status", "exception", "null", "crash"],
            "state update defect": ["status", "state", "pending", "updated", "wrong"],
        },
        "steps": [
            "Reproduce the issue with the smallest failing input.",
            "Compare actual behavior against the expected API or workflow contract.",
            "Inspect validation, middleware, and error-handling paths around the affected component.",
            "Add a regression test that captures the failing input condition.",
        ],
    },
    "requirement_gap": {
        "default": "missing or ambiguous expected behavior",
        "signals": {
            "undefined acceptance criteria": ["acceptance", "criteria", "expected", "behavior", "unclear"],
            "conflicting product or API requirement": ["conflict", "disagree", "spec", "ux", "document"],
            "missing role or workflow rule": ["role", "approval", "threshold", "permission"],
        },
        "steps": [
            "Identify the missing or conflicting requirement statement.",
            "Ask product/engineering owner to define expected behavior and edge cases.",
            "Convert the clarified rule into acceptance criteria.",
            "Add test cases that lock the clarified behavior.",
        ],
    },
    "test_environment_issue": {
        "default": "environment, configuration, or dependency mismatch",
        "signals": {
            "staging/local configuration mismatch": ["staging", "local", "environment", "config"],
            "external dependency unavailable": ["sandbox", "endpoint", "network", "dns", "callback"],
            "test runner setup problem": ["ci", "container", "runner", "driver", "timezone"],
        },
        "steps": [
            "Compare local, CI, and staging configuration values.",
            "Check dependent service availability, credentials, callbacks, and network routes.",
            "Re-run the failing test after isolating environment-only variables.",
            "Document environment assumptions in the test setup.",
        ],
    },
    "data_issue": {
        "default": "missing, malformed, duplicated, or inconsistent data",
        "signals": {
            "schema or format inconsistency": ["format", "mixed", "schema", "field", "timestamp"],
            "duplicate or missing records": ["duplicate", "missing", "null", "blank"],
            "import or migration data defect": ["csv", "import", "migration", "trimmed"],
        },
        "steps": [
            "Inspect the source records behind the failing output.",
            "Validate schema, null values, duplicates, and format consistency.",
            "Trace the import or transformation step that produced the bad data.",
            "Add data validation checks before model or report consumption.",
        ],
    },
    "performance_issue": {
        "default": "latency, throughput, memory, or scaling bottleneck",
        "signals": {
            "slow query or API latency": ["slow", "latency", "seconds", "timeout", "duration"],
            "large dataset scaling issue": ["100k", "large", "rows", "records", "batch"],
            "resource consumption issue": ["memory", "cpu", "unresponsive", "gateway"],
        },
        "steps": [
            "Measure latency and resource usage on the failing path.",
            "Identify whether the bottleneck is query, API, network, or rendering related.",
            "Compare performance on small and large datasets.",
            "Add a performance regression benchmark for the workload.",
        ],
    },
    "integration_issue": {
        "default": "API contract, authentication, webhook, or service synchronization mismatch",
        "signals": {
            "API field contract mismatch": ["customerid", "customer_id", "field", "expects", "contract"],
            "authentication or registration issue": ["oauth", "token", "secret", "azure", "registration"],
            "webhook or synchronization issue": ["webhook", "sync", "synchronized", "service", "idempotency"],
        },
        "steps": [
            "Compare producer and consumer API contracts for field names, types, and status semantics.",
            "Check auth credentials, token audience, secrets, and callback registration.",
            "Inspect retry/idempotency handling for duplicated or missed events.",
            "Add contract tests between the integrated systems.",
        ],
    },
}


SUITE_CONTEXT = {
    "module": "IssueSense ML",
    "suite": "Engineering Intelligence Suite",
    "role": "AI triage engine for engineering issue classification and root-cause inspection.",
    "upstream": "Issue Intake receives bug reports, test findings, validation failures, logs, or incident notes.",
    "downstream": [
        "EngiAgent can expand high-confidence findings into evidence-grounded investigation or 8D drafts.",
        "QAForge AI can convert confirmed requirement or defect risks into requirement-linked test cases.",
    ],
}


def build_triage_details(text: str, predicted_label: str, confidence: float, status: str, evidence_matches: int) -> dict:
    rule = CAUSE_RULES[predicted_label]
    normalized = normalize_text(text)
    cause, matched_terms = infer_cause(normalized, rule)
    rationale = build_rationale(predicted_label, confidence, status, evidence_matches, cause, matched_terms)
    return {
        "likely_cause": cause,
        "cause_rationale": rationale,
        "next_investigation_steps": rule["steps"],
        "suite_context": SUITE_CONTEXT,
    }


def infer_cause(normalized_text: str, rule: dict) -> tuple[str, list[str]]:
    for cause, terms in rule["signals"].items():
        matched = [term for term in terms if term in normalized_text]
        if matched:
            return cause, matched
    return rule["default"], []


def build_rationale(
    predicted_label: str,
    confidence: float,
    status: str,
    evidence_matches: int,
    cause: str,
    matched_terms: list[str],
) -> str:
    confidence_text = f"{confidence:.2f}"
    if status == "needs_review":
        return (
            f"The model's best guess is {predicted_label}, but it is marked for review. "
            f"Likely cause is '{cause}' with confidence {confidence_text}; "
            f"{evidence_matches} retrieved evidence item(s) matched the predicted label."
        )
    signal_text = f" Signals: {', '.join(matched_terms)}." if matched_terms else ""
    return (
        f"The finding is classified as {predicted_label} with confidence {confidence_text}. "
        f"The likely cause is '{cause}' based on the issue wording and retrieved evidence."
        f"{signal_text}"
    )
