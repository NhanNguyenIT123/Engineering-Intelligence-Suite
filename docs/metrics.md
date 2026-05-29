# IssueSense ML Metrics

Generated on: 2026-05-29

Environment:

- Python: 3.12.13 via local virtual environment
- PyTorch training device: CUDA
- GPU: NVIDIA RTX 3050 6GB Laptop GPU

Dataset:

- Source: synthetic/curated educational templates
- Total records: 360
- Labels: 6
- Train / validation / test: 252 / 54 / 54
- Class balance: 60 records per class

Model comparison:

| Model | Test accuracy | Test macro F1 | Average latency |
| --- | ---: | ---: | ---: |
| TF-IDF + Logistic Regression | 1.000 | 1.000 | 0.035 ms/sample |
| PyTorch TextCNN | 1.000 | 1.000 | 0.193 ms/sample |

Confusion matrix label order:

1. `software_bug`
2. `requirement_gap`
3. `test_environment_issue`
4. `data_issue`
5. `performance_issue`
6. `integration_issue`

Current test confusion matrix for both models:

```text
[[9, 0, 0, 0, 0, 0],
 [0, 9, 0, 0, 0, 0],
 [0, 0, 9, 0, 0, 0],
 [0, 0, 0, 9, 0, 0],
 [0, 0, 0, 0, 9, 0],
 [0, 0, 0, 0, 0, 9]]
```

Interpretation:

- These metrics prove the local ML pipeline works end to end.
- The numbers are high because the current dataset is generated from controlled engineering templates.
- Before using the project as a stronger CV claim, add a manually reviewed challenge set with noisier mixed wording and report metrics separately.
