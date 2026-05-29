# IssueSense ML Metrics

Generated on: 2026-05-29

Environment:

- Python: 3.12.13 via local virtual environment
- PyTorch training device: CUDA
- GPU: NVIDIA RTX 3050 6GB Laptop GPU

Dataset:

- Source: synthetic/curated educational templates
- Total records: 540
- Labels: 6
- Train / validation / test: 378 / 81 / 81
- Class balance: 90 records per class

Challenge dataset:

- Source: manually written challenge examples
- Total records: 36
- Class balance: 6 records per class
- Purpose: test noisier, less template-like wording that is not used for training

Synthetic test comparison:

| Model | Test accuracy | Test macro F1 | Average latency |
| --- | ---: | ---: | ---: |
| TF-IDF + Logistic Regression | 1.000 | 1.000 | 0.023 ms/sample |
| PyTorch TextCNN | 1.000 | 1.000 | 0.116 ms/sample |

Manual challenge comparison:

| Model | Challenge accuracy | Challenge macro F1 | Average latency |
| --- | ---: | ---: | ---: |
| TF-IDF + Logistic Regression | 0.972 | 0.972 | 0.036 ms/sample |
| PyTorch TextCNN | 0.861 | 0.863 | 0.089 ms/sample |

Confusion matrix label order:

1. `software_bug`
2. `requirement_gap`
3. `test_environment_issue`
4. `data_issue`
5. `performance_issue`
6. `integration_issue`

Synthetic test confusion matrix for both models:

```text
[[14, 0, 0, 0, 0, 0],
 [0, 14, 0, 0, 0, 0],
 [0, 0, 13, 0, 0, 0],
 [0, 0, 0, 13, 0, 0],
 [0, 0, 0, 0, 14, 0],
 [0, 0, 0, 0, 0, 13]]
```

Interpretation:

- These metrics prove the local ML pipeline works end to end.
- Synthetic-test scores are high because the generated dataset is controlled and class-balanced.
- The manual challenge split is the more honest interview metric because it uses noisier examples that were not used during training.
- TF-IDF is currently stronger on the small challenge set. The PyTorch TextCNN still demonstrates model training, GPU usage, and error analysis, but needs more manually reviewed data to generalize further.
