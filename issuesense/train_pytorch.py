import json
import time

import torch
from sklearn.metrics import accuracy_score, f1_score
from torch import nn
from torch.utils.data import DataLoader

from issuesense.data import load_records, split_records, texts_and_labels
from issuesense.labels import LABELS
from issuesense.paths import MODEL_DIR, TEXTCNN_MODEL_PATH
from issuesense.textcnn import TextCNN
from issuesense.torch_data import IssueDataset, build_vocab


def evaluate_loader(model: TextCNN, loader: DataLoader, device: torch.device) -> tuple[float, float]:
    model.eval()
    labels = []
    predictions = []
    with torch.no_grad():
        for input_ids, batch_labels in loader:
            logits = model(input_ids.to(device))
            predictions.extend(torch.argmax(logits, dim=1).cpu().tolist())
            labels.extend(batch_labels.tolist())
    return accuracy_score(labels, predictions), f1_score(labels, predictions, average="macro")


def main() -> None:
    torch.manual_seed(42)
    records = load_records()
    train_records, validation_records, test_records = split_records(records)
    train_texts, train_labels = texts_and_labels(train_records)
    validation_texts, validation_labels = texts_and_labels(validation_records)
    test_texts, test_labels = texts_and_labels(test_records)

    vocab = build_vocab(train_texts, min_freq=1)
    train_loader = DataLoader(IssueDataset(train_texts, train_labels, vocab), batch_size=32, shuffle=True)
    validation_loader = DataLoader(IssueDataset(validation_texts, validation_labels, vocab), batch_size=64)
    test_loader = DataLoader(IssueDataset(test_texts, test_labels, vocab), batch_size=64)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = TextCNN(vocab_size=len(vocab), num_classes=len(LABELS)).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.002, weight_decay=0.01)
    loss_fn = nn.CrossEntropyLoss()

    best_macro_f1 = -1.0
    best_state = None
    started = time.perf_counter()
    history = []

    for epoch in range(1, 9):
        model.train()
        total_loss = 0.0
        for input_ids, labels in train_loader:
            input_ids = input_ids.to(device)
            labels = labels.to(device)
            optimizer.zero_grad()
            loss = loss_fn(model(input_ids), labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        validation_accuracy, validation_macro_f1 = evaluate_loader(model, validation_loader, device)
        history.append(
            {
                "epoch": epoch,
                "loss": total_loss / max(len(train_loader), 1),
                "validation_accuracy": validation_accuracy,
                "validation_macro_f1": validation_macro_f1,
            }
        )
        print(json.dumps(history[-1], indent=2))

        if validation_macro_f1 > best_macro_f1:
            best_macro_f1 = validation_macro_f1
            best_state = model.state_dict()

    if best_state is not None:
        model.load_state_dict(best_state)
    test_accuracy, test_macro_f1 = evaluate_loader(model, test_loader, device)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state": model.state_dict(),
            "vocab": vocab,
            "labels": LABELS,
            "max_length": 64,
            "history": history,
            "test_accuracy": test_accuracy,
            "test_macro_f1": test_macro_f1,
            "device": str(device),
            "training_seconds": time.perf_counter() - started,
        },
        TEXTCNN_MODEL_PATH,
    )
    print(f"Saved PyTorch model to {TEXTCNN_MODEL_PATH}")
    print(json.dumps({"test_accuracy": test_accuracy, "test_macro_f1": test_macro_f1, "device": str(device)}, indent=2))


if __name__ == "__main__":
    main()
