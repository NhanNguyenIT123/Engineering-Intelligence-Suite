import csv
import random

from issuesense.paths import DATASET_PATH, PROCESSED_DIR


TEMPLATES = {
    "software_bug": [
        "The {module} returns HTTP 500 when {condition}, expected {expected} and the issue is reproducible in regression testing.",
        "{module} crashes after {action}; logs show null reference and the user cannot complete the workflow.",
        "After the latest build, {module} saves an incorrect value when {condition}, but the previous release worked.",
        "The button in {module} triggers the wrong API endpoint and updates a different record.",
        "{module} accepts invalid input and still returns success, causing incorrect state in the application.",
        "The calculation in {module} is off by one when {condition}, confirmed with three repeated runs.",
    ],
    "requirement_gap": [
        "The expected behavior for {module} is not defined when {condition}; QA cannot decide whether this is a defect.",
        "Acceptance criteria mention {action}, but do not specify validation rules for {condition}.",
        "Product notes conflict with the API contract for {module}; one says allow the flow and another says block it.",
        "The user story for {module} has no error-state requirement when the downstream service is unavailable.",
        "There is no requirement describing which role can perform {action} in {module}.",
        "The design mockup and requirement document disagree about the message shown after {action}.",
    ],
    "test_environment_issue": [
        "The failure happens only on staging because {dependency} is configured with an expired certificate.",
        "{module} passes locally but fails in CI after the test container cannot reach {dependency}.",
        "Regression tests fail because the environment variable for {dependency} is missing in the test runner.",
        "The staging database was restored from an old snapshot, so {module} cannot find required fixtures.",
        "The test run is blocked because the mock server for {dependency} returns connection refused.",
        "{module} fails only on the QA machine where the browser driver version does not match the runtime.",
    ],
    "data_issue": [
        "{module} shows duplicated records because the imported CSV contains repeated customer identifiers.",
        "The report is incorrect because required field {field} is empty for several rows in the dataset.",
        "The pipeline rejects the batch after {field} contains malformed values and unexpected whitespace.",
        "{module} cannot render the dashboard because the source data has mixed date formats.",
        "Search results are missing because the indexed dataset does not include recently migrated records.",
        "The model output is unstable because labels in the training file are inconsistent for similar examples.",
    ],
    "performance_issue": [
        "{module} takes {duration} to load when the dataset has more than {count} records.",
        "The API times out during {action}; CPU usage stays above {measure} for the whole request.",
        "Memory usage grows after every refresh in {module}, and the browser becomes unresponsive.",
        "The query plan for {module} performs a full table scan and exceeds the latency budget.",
        "Batch processing slows down after {count} records and the worker misses the scheduled window.",
        "{module} responds in {duration} on staging while the requirement is under 1s.",
    ],
    "integration_issue": [
        "{module} fails after {dependency} changes the response field from statusCode to status_code.",
        "The webhook integration sends the event twice and the downstream service creates duplicate tickets.",
        "OAuth callback from {dependency} returns success but the token audience does not match our API.",
        "{module} cannot sync because the third-party API now requires an additional header.",
        "The payment sandbox accepts the request, but our service cannot parse the nested error payload.",
        "The message queue contract changed and {module} still publishes the old event schema.",
    ],
}

MODULES = [
    "login API",
    "booking workflow",
    "reporting dashboard",
    "candidate ranking service",
    "notification worker",
    "file import module",
    "admin panel",
    "search endpoint",
]
CONDITIONS = [
    "the password contains special characters",
    "the input date is at month end",
    "the user has a reviewer role",
    "the request contains Vietnamese characters",
    "the payload has an optional field",
    "the network is slow",
]
ACTIONS = [
    "submitting the form",
    "exporting the report",
    "approving the request",
    "syncing records",
    "uploading a document",
    "refreshing the dashboard",
]
DEPENDENCIES = ["SharePoint mock API", "PostgreSQL service", "OAuth provider", "email gateway", "S3-compatible storage", "message broker"]
FIELDS = ["email", "created_at", "candidate_score", "status", "external_id", "department_code"]
EXPECTED = ["HTTP 401", "a validation error", "a retryable failure", "an empty-state message", "a warning banner"]
DURATIONS = ["4.8s", "9200ms", "12 seconds", "6.5s", "15000ms"]
COUNTS = ["10,000", "50,000", "250,000", "1,000,000"]
MEASURES = ["85%", "92%", "1.5GB", "700MB"]


def render(template: str, rng: random.Random) -> str:
    return template.format(
        module=rng.choice(MODULES),
        condition=rng.choice(CONDITIONS),
        action=rng.choice(ACTIONS),
        dependency=rng.choice(DEPENDENCIES),
        field=rng.choice(FIELDS),
        expected=rng.choice(EXPECTED),
        duration=rng.choice(DURATIONS),
        count=rng.choice(COUNTS),
        measure=rng.choice(MEASURES),
    )


def main() -> None:
    rng = random.Random(42)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    row_id = 1
    for label, templates in TEMPLATES.items():
        for _ in range(60):
            text = render(rng.choice(templates), rng)
            rows.append(
                {
                    "id": f"ISSUE-{row_id:04d}",
                    "text": text,
                    "label": label,
                    "source": "synthetic_curated_template",
                }
            )
            row_id += 1

    rng.shuffle(rows)
    with DATASET_PATH.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["id", "text", "label", "source"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} records to {DATASET_PATH}")


if __name__ == "__main__":
    main()
