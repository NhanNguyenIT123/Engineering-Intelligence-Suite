import csv
from dataclasses import dataclass
from pathlib import Path

from sklearn.model_selection import train_test_split

from issuesense.labels import LABEL_TO_ID
from issuesense.paths import DATASET_PATH
from issuesense.preprocessing import normalize_text


@dataclass(frozen=True)
class IssueRecord:
    id: str
    text: str
    label: str
    source: str


def load_records(path: Path = DATASET_PATH) -> list[IssueRecord]:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at {path}. Run: python -m issuesense.generate_dataset")

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        records = [
            IssueRecord(
                id=row["id"],
                text=row["text"],
                label=row["label"],
                source=row.get("source", "synthetic"),
            )
            for row in reader
        ]

    unknown = sorted({record.label for record in records if record.label not in LABEL_TO_ID})
    if unknown:
        raise ValueError(f"Unknown labels in dataset: {unknown}")
    return records


def split_records(records: list[IssueRecord], seed: int = 42):
    labels = [record.label for record in records]
    train_records, temp_records = train_test_split(
        records,
        test_size=0.30,
        random_state=seed,
        stratify=labels,
    )
    temp_labels = [record.label for record in temp_records]
    validation_records, test_records = train_test_split(
        temp_records,
        test_size=0.50,
        random_state=seed,
        stratify=temp_labels,
    )
    return train_records, validation_records, test_records


def texts_and_labels(records: list[IssueRecord]) -> tuple[list[str], list[int]]:
    texts = [normalize_text(record.text) for record in records]
    labels = [LABEL_TO_ID[record.label] for record in records]
    return texts, labels
