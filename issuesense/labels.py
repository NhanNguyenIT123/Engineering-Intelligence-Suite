LABELS = [
    "software_bug",
    "requirement_gap",
    "test_environment_issue",
    "data_issue",
    "performance_issue",
    "integration_issue",
]

LABEL_DESCRIPTIONS = {
    "software_bug": "A reproducible implementation defect or broken application behavior.",
    "requirement_gap": "Missing, unclear, conflicting, or incomplete expected behavior.",
    "test_environment_issue": "A setup, staging, dependency, network, or configuration problem in the test environment.",
    "data_issue": "Missing, malformed, duplicated, inconsistent, or stale data.",
    "performance_issue": "Latency, timeout, throughput, memory, CPU, or resource usage problem.",
    "integration_issue": "API contract, auth, webhook, third-party, or service integration mismatch.",
}

LABEL_TO_ID = {label: index for index, label in enumerate(LABELS)}
ID_TO_LABEL = {index: label for label, index in LABEL_TO_ID.items()}
