import json
import time
from collections import Counter

import joblib
import torch
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

from issuesense.data import load_records, split_records, texts_and_labels
from issuesense.labels import LABELS
from issuesense.paths import BASELINE_MODEL_PATH, METRICS_PATH, OUTPUT_DIR, TEXTCNN_MODEL_PATH
from issuesense.textcnn import TextCNN
from issuesense.torch_data import encode_text


def evaluate_baseline(texts: list[str], labels: list[int]) -> dict:
    model = joblib.load(BASELINE_MODEL_PATH)
    started = time.perf_counter()
    predictions = model.predict(texts)
    elapsed = time.perf_counter() - started
    return build_metrics("tfidf_logistic_regression", labels, predictions, elapsed, len(texts))


def evaluate_textcnn(texts: list[str], labels: list[int]) -> dict:
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
    return metrics


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


def main() -> None:
    records = load_records()
    train_records, validation_records, test_records = split_records(records)
    test_texts, test_labels = texts_and_labels(test_records)

    metrics = {
        "dataset": {
            "total_records": len(records),
            "train_records": len(train_records),
            "validation_records": len(validation_records),
            "test_records": len(test_records),
            "label_distribution": dict(Counter(record.label for record in records)),
            "source": "synthetic_curated_template",
        },
        "models": [
            evaluate_baseline(test_texts, test_labels),
            evaluate_textcnn(test_texts, test_labels),
        ],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    print(f"Wrote metrics to {METRICS_PATH}")


if __name__ == "__main__":
    main()
