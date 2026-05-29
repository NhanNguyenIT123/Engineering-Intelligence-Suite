# Evaluation Notes

Run the full benchmark with:

```powershell
python -m issuesense.evaluate
```

Generated artifacts:

- `outputs/metrics.json`: dataset size, per-model accuracy, macro F1, latency, and confusion matrices.
- `models/baseline.joblib`: TF-IDF + Logistic Regression baseline.
- `models/textcnn.pt`: PyTorch TextCNN checkpoint.
- `data/processed/issues.csv`: generated synthetic/curated dataset.

The dataset is synthetic/curated for educational portfolio use. Metrics should be reported honestly with the dataset size and label distribution.

The latest committed metric summary is in `docs/metrics.md`. The machine-readable runtime output is generated at `outputs/metrics.json`.
