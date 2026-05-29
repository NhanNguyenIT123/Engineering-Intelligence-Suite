# Optional LLM Explanation

IssueSense ML does not use an LLM as the classifier.

The classifier is:

- TF-IDF + Logistic Regression baseline, or
- PyTorch TextCNN

The optional LLM layer is only used to rewrite an explanation from retrieved examples.

## Provider

Default:

```text
ISSUESENSE_EXPLANATION_PROVIDER=extractive
```

Optional:

```text
ISSUESENSE_EXPLANATION_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:1.5b-instruct
OLLAMA_BASE_URL=http://127.0.0.1:11434
```

## Guardrails

LLM explanations are accepted only when:

- the output has enough text,
- it mentions the predicted label,
- it overlaps with retrieved evidence terms.

If the output fails these checks or Ollama is unavailable, the system falls back to the extractive explanation.

This avoids overclaiming and keeps similar labeled examples as the source of truth.
