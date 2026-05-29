# Model Card

## Intended Use

IssueSense ML classifies short engineering issue reports and test-report findings into triage categories:

- software defect
- requirement gap
- test environment issue
- data issue
- performance issue
- integration issue

The project is intended as an educational AI/ML portfolio prototype, not a production incident-routing system.

## Model Family

- Baseline: TF-IDF features with Logistic Regression.
- Neural model: PyTorch TextCNN with trainable word embeddings.

## Data

- Training data is generated from synthetic/curated engineering templates.
- Challenge data is manually written to include noisier wording, overlapping terms, and less template-like reports.
- Labels are balanced to make early model comparison easier.

## Evaluation

The evaluation reports two splits:

- `synthetic_test`: held-out samples from the generated dataset.
- `manual_challenge`: manually written challenge samples committed under `data/challenge`.

The challenge split is more important for interview discussion because it is closer to realistic QA/engineering wording.

## Limitations

- The dataset is still small and not collected from a real enterprise issue tracker.
- High synthetic-test performance does not prove production generalization.
- The model may confuse software bugs with integration issues when API behavior and implementation behavior overlap.
- The model does not perform root-cause analysis; it predicts a triage category and retrieves similar examples for explanation.

## Next Improvements

- Add 200+ manually reviewed issue reports with noisier wording.
- Track per-class confusion on a larger challenge set.
- Add active-learning review workflow for uncertain predictions.
- Add sentence-transformer embeddings for better similar-example retrieval.
