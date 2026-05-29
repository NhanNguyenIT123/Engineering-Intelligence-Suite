# Uncertainty Handling

IssueSense ML should not pretend that every short text can be classified reliably.

The API returns two possible statuses:

- `auto_classified`: confidence, input length, and retrieved evidence are strong enough for a direct classification.
- `needs_review`: the model still returns a best guess, but the UI marks the result as requiring human review.

Current review triggers:

- Input has fewer than 6 normalized tokens.
- Model confidence is below `0.55`.
- Retrieved similar examples do not match the predicted label.

Example:

```text
500 Server error
```

This is too short. It may be a software defect, integration failure, infrastructure issue, or incomplete report. The system should show a best guess plus review reasons instead of pretending the label is certain.

Better input:

```text
During regression testing, the login API returns HTTP 500 only when the password contains special characters. Expected HTTP 401 for invalid credentials.
```

This contains component, condition, actual behavior, and expected behavior, so the classifier can make a more defensible prediction.
