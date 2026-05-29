# Error Analysis

## synthetic_test

### tfidf_logistic_regression

No misclassifications in this split.

### pytorch_textcnn

No misclassifications in this split.

## manual_challenge

### tfidf_logistic_regression

- `CH-0033` expected `integration_issue`, predicted `software_bug`
  - The Teams notification flow fails after the app registration secret expired in Azure.

### pytorch_textcnn

- `CH-0009` expected `requirement_gap`, predicted `test_environment_issue`
  - The API spec allows empty attachment lists, while the UX document marks attachment as mandatory.
- `CH-0012` expected `requirement_gap`, predicted `performance_issue`
  - The expected behavior is unclear when a device submits duplicate telemetry within the same second.
- `CH-0014` expected `test_environment_issue`, predicted `integration_issue`
  - Staging cannot reproduce the bug after the mock payment service was restarted with the wrong sandbox account.
- `CH-0021` expected `data_issue`, predicted `test_environment_issue`
  - The training file contains near-duplicate issue descriptions with conflicting labels.
- `CH-0033` expected `integration_issue`, predicted `test_environment_issue`
  - The Teams notification flow fails after the app registration secret expired in Azure.

## Findings

- TF-IDF handles the small challenge set better because word and phrase overlap is highly informative for these short issue reports.
- TextCNN improved after adding broader engineering templates, but it still confuses requirement, environment, and integration cases when the report contains mixed signals.
- The next useful improvement is not a larger neural model first; it is a larger manually reviewed dataset and better uncertain-prediction handling.
