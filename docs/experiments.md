# Experiment Tracking

IssueSense ML records evaluation runs in JSONL format:

```text
outputs/experiments/runs.jsonl
```

Each run contains:

- `run_id`
- `created_at`
- synthetic dataset hash
- challenge dataset hash
- dataset sizes
- model metrics for `synthetic_test`
- model metrics for `manual_challenge`

This makes the project easier to discuss in interviews because model performance is tied to a dataset version instead of being a single unexplained number.

Current tracked metrics include:

- accuracy
- macro F1
- average latency per sample

Generated artifacts are intentionally ignored by Git. Reproduce them with:

```powershell
.\scripts\run_pipeline.ps1
```
