import argparse
import json
import time

import joblib
import torch

from issuesense.explain import build_explanation
from issuesense.labels import ID_TO_LABEL, LABELS
from issuesense.paths import BASELINE_MODEL_PATH, TEXTCNN_MODEL_PATH
from issuesense.preprocessing import normalize_text
from issuesense.textcnn import TextCNN
from issuesense.torch_data import encode_text


def predict_baseline(text: str) -> dict:
    if not BASELINE_MODEL_PATH.exists():
        raise FileNotFoundError("Baseline model missing. Run: python -m issuesense.train_baseline")
    model = joblib.load(BASELINE_MODEL_PATH)
    started = time.perf_counter()
    probabilities = model.predict_proba([normalize_text(text)])[0]
    label_id = int(probabilities.argmax())
    return {
        "model": "tfidf_logistic_regression",
        "label": ID_TO_LABEL[label_id],
        "confidence": float(probabilities[label_id]),
        "latency_ms": (time.perf_counter() - started) * 1000,
    }


def predict_textcnn(text: str) -> dict:
    if not TEXTCNN_MODEL_PATH.exists():
        raise FileNotFoundError("PyTorch model missing. Run: python -m issuesense.train_pytorch")
    checkpoint = torch.load(TEXTCNN_MODEL_PATH, map_location="cpu")
    vocab = checkpoint["vocab"]
    max_length = checkpoint["max_length"]
    model = TextCNN(vocab_size=len(vocab), num_classes=len(LABELS))
    model.load_state_dict(checkpoint["model_state"])
    model.eval()

    input_ids = torch.tensor([encode_text(text, vocab, max_length)], dtype=torch.long)
    started = time.perf_counter()
    with torch.no_grad():
        probabilities = torch.softmax(model(input_ids), dim=1)[0]
    label_id = int(torch.argmax(probabilities).item())
    return {
        "model": "pytorch_textcnn",
        "label": ID_TO_LABEL[label_id],
        "confidence": float(probabilities[label_id].item()),
        "latency_ms": (time.perf_counter() - started) * 1000,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("text", help="Engineering issue or test-report finding to classify.")
    parser.add_argument("--model", choices=["baseline", "textcnn"], default="textcnn")
    args = parser.parse_args()

    prediction = predict_textcnn(args.text) if args.model == "textcnn" else predict_baseline(args.text)
    prediction["explanation"] = build_explanation(args.text, prediction["label"], prediction["confidence"])
    print(json.dumps(prediction, indent=2))


if __name__ == "__main__":
    main()
