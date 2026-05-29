import json
import time
from collections import Counter

import joblib
import torch
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

from issuesense.data import IssueRecord, load_challenge_records, load_records, split_records, texts_and_labels
from issuesense.experiment_tracking import append_run
from issuesense.labels import LABELS
from issuesense.paths import BASELINE_MODEL_PATH, ERROR_ANALYSIS_PATH, METRICS_PATH, OUTPUT_DIR, TEXTCNN_MODEL_PATH
from issuesense.textcnn import TextCNN
from issuesense.torch_data import encode_text


def evaluate_baseline(texts: list[str], labels: list[int]) -> tuple[dict, list[int]]:
    model = joblib.load(BASELINE_MODEL_PATH)
    started = time.perf_counter()
    predictions = model.predict(texts).tolist()
    elapsed = time.perf_counter() - started
    return build_metrics("tfidf_logistic_regression", labels, predictions, elapsed, len(texts)), predictions


def evaluate_textcnn(texts: list[str], labels: list[int]) -> tuple[dict, list[int]]:
    checkpoint = torch.load(TEXTCNN_MODEL_PATH, map_location="cpu")
    vocab = checkpoint["vocab"]
    model = TextCNN(vocab_size=len(vocab), num_classes=len(LABELS))
    model.load_state_dict(checkpoint["model_state"])
    model.eval()

    encoded = torch.tensor([encode_text(text, vocab, checkpoint["max_length"]) for text in texts], dtype=torch.long)
    started = time.perf_counter()
    with torch.no_grad():
        predictions = torch.argmax(model(encoded), dim=1).tolist()
    elapsed = time.perf_counter() - started
    metrics = build_metrics("pytorch_textcnn", labels, predictions, elapsed, len(texts))
    metrics["training_device"] = checkpoint.get("device", "unknown")
    metrics["training_seconds"] = checkpoint.get("training_seconds")
    return metrics, predictions


def build_metrics(model_name: str, labels: list[int], predictions: list[int], elapsed: float, total: int) -> dict:
    return {
        "model": model_name,
        "accuracy": accuracy_score(labels, predictions),
        "macro_f1": f1_score(labels, predictions, average="macro"),
        "avg_latency_ms": (elapsed / max(total, 1)) * 1000,
        "classification_report": classification_report(
            labels,
            predictions,
            target_names=LABELS,
            output_dict=True,
            zero_division=0,
        ),
        "confusion_matrix": confusion_matrix(labels, predictions).tolist(),
    }


def evaluate_split(name: str, records: list[IssueRecord]) -> dict:
    texts, labels = texts_and_labels(records)
    baseline_metrics, baseline_predictions = evaluate_baseline(texts, labels)
    textcnn_metrics, textcnn_predictions = evaluate_textcnn(texts, labels)
    return {
        "name": name,
        "records": len(records),
        "models": [baseline_metrics, textcnn_metrics],
        "error_analysis": {
            "tfidf_logistic_regression": collect_errors(records, labels, baseline_predictions),
            "pytorch_textcnn": collect_errors(records, labels, textcnn_predictions),
        },
    }


def collect_errors(records: list[IssueRecord], labels: list[int], predictions: list[int], limit: int = 12) -> list[dict]:
    errors = []
    for record, expected_id, predicted_id in zip(records, labels, predictions):
        if expected_id != predicted_id:
            errors.append(
                {
                    "id": record.id,
                    "expected": LABELS[expected_id],
                    "predicted": LABELS[predicted_id],
                    "text": record.text,
                }
            )
    return errors[:limit]


def write_error_analysis(metrics: dict) -> None:
    lines = ["# Error Analysis", ""]
    for split in metrics["evaluation_splits"]:
        lines.append(f"## {split['name']}")
        lines.append("")
        for model_name, errors in split["error_analysis"].items():
            lines.append(f"### {model_name}")
            lines.append("")
            if not errors:
                lines.append("No misclassifications in this split.")
                lines.append("")
                continue
            for error in errors:
                lines.append(f"- `{error['id']}` expected `{error['expected']}`, predicted `{error['predicted']}`")
                lines.append(f"  - {error['text']}")
            lines.append("")
    ERROR_ANALYSIS_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    records = load_records()
    train_records, validation_records, test_records = split_records(records)
    challenge_records = load_challenge_records()

    metrics = {
        "dataset": {
            "total_records": len(records),
            "train_records": len(train_records),
            "validation_records": len(validation_records),
            "test_records": len(test_records),
            "label_distribution": dict(Counter(record.label for record in records)),
            "source": "synthetic_curated_template",
        },
        "challenge_dataset": {
            "total_records": len(challenge_records),
            "label_distribution": dict(Counter(record.label for record in challenge_records)),
            "source": "manual_reviewed_challenge",
        },
        "evaluation_splits": [
            evaluate_split("synthetic_test", test_records),
            evaluate_split("manual_challenge", challenge_records),
        ],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    run_record = append_run(metrics)
    metrics["experiment_run"] = run_record
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    write_error_analysis(metrics)
    print(json.dumps(metrics, indent=2))
    print(f"Wrote metrics to {METRICS_PATH}")
    print(f"Wrote error analysis to {ERROR_ANALYSIS_PATH}")


if __name__ == "__main__":
    main()
