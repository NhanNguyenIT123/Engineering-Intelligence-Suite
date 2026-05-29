import json

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.pipeline import Pipeline

from issuesense.data import load_records, split_records, texts_and_labels
from issuesense.labels import LABELS
from issuesense.paths import BASELINE_MODEL_PATH, MODEL_DIR, OUTPUT_DIR


def main() -> None:
    records = load_records()
    train_records, validation_records, _ = split_records(records)
    train_texts, train_labels = texts_and_labels(train_records)
    validation_texts, validation_labels = texts_and_labels(validation_records)

    model = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2)),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )
    model.fit(train_texts, train_labels)
    predictions = model.predict(validation_texts)

    metrics = {
        "validation_accuracy": accuracy_score(validation_labels, predictions),
        "validation_macro_f1": f1_score(validation_labels, predictions, average="macro"),
        "classification_report": classification_report(
            validation_labels,
            predictions,
            target_names=LABELS,
            output_dict=True,
            zero_division=0,
        ),
    }

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, BASELINE_MODEL_PATH)

    print(json.dumps(metrics, indent=2))
    print(f"Saved baseline model to {BASELINE_MODEL_PATH}")


if __name__ == "__main__":
    main()
