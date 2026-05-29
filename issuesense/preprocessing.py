import re


def normalize_text(text: str) -> str:
    """Normalize noisy issue text without removing engineering signals."""
    normalized = text.lower()
    normalized = re.sub(r"\b[1-5]\d{2}\b", " http_status ", normalized)
    normalized = re.sub(r"\b\d+(\.\d+)?\s?(ms|s|sec|seconds)\b", " duration ", normalized)
    normalized = re.sub(r"\b\d+(\.\d+)?\s?(mb|gb|kb)\b|\b\d+(\.\d+)?%", " measure ", normalized)
    normalized = re.sub(r"[^a-z0-9_]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def tokenize(text: str) -> list[str]:
    return normalize_text(text).split()
