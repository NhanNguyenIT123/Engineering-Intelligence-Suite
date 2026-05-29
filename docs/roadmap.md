# Roadmap

IssueSense ML is structured as a portfolio project with staged depth, not a one-file demo.

## Phase 1 - ML Baseline

- Generate a balanced synthetic/curated engineering issue dataset.
- Implement preprocessing and train/validation/test split.
- Train TF-IDF + Logistic Regression baseline.
- Track accuracy, macro F1, latency, and confusion matrix.

## Phase 2 - PyTorch Model

- Implement TextCNN classifier with trainable embeddings.
- Train on local GPU when available.
- Compare neural model against the baseline.
- Save model checkpoint and prediction CLI.

## Phase 3 - Challenge Evaluation

- Add manually written challenge examples that are not used for training.
- Report synthetic-test and manual-challenge metrics separately.
- Document misclassifications and realistic model limitations.

## Phase 4 - Product Demo

- Build Streamlit dashboard with classifier controls, model comparison, error analysis, and explanation evidence.
- Add similar-example retrieval to make predictions easier to inspect.
- Keep generated artifacts out of Git while committing reproducible scripts and docs.

## Next Phase

- Add 200+ manually reviewed challenge/training examples.
- Add uncertainty thresholding and human-review routing.
- Add sentence-transformer retrieval for better explanation evidence.
- Add experiment tracking across dataset versions.
