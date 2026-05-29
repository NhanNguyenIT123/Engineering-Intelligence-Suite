import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from issuesense.paths import CHALLENGE_DATASET_PATH, DATASET_PATH, EXPERIMENT_DIR, EXPERIMENT_LOG_PATH


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def build_run_record(metrics: dict) -> dict:
    return {
        "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "dataset_version": {
            "synthetic_sha256": file_sha256(DATASET_PATH),
            "challenge_sha256": file_sha256(CHALLENGE_DATASET_PATH),
            "synthetic_records": metrics["dataset"]["total_records"],
            "challenge_records": metrics["challenge_dataset"]["total_records"],
        },
        "summary": summarize_metrics(metrics),
    }


def summarize_metrics(metrics: dict) -> dict:
    summary = {}
    for split in metrics["evaluation_splits"]:
        summary[split["name"]] = {
            model["model"]: {
                "accuracy": model["accuracy"],
                "macro_f1": model["macro_f1"],
                "avg_latency_ms": model["avg_latency_ms"],
            }
            for model in split["models"]
        }
    return summary


def append_run(metrics: dict) -> dict:
    EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)
    record = build_run_record(metrics)
    with EXPERIMENT_LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")
    return record


def load_runs(limit: int = 20) -> list[dict]:
    if not EXPERIMENT_LOG_PATH.exists():
        return []
    lines = EXPERIMENT_LOG_PATH.read_text(encoding="utf-8").splitlines()
    runs = [json.loads(line) for line in lines if line.strip()]
    return runs[-limit:]
