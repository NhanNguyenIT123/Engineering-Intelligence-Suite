from dataclasses import asdict
import json
import os
import urllib.error
import urllib.request

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from issuesense.data import IssueRecord, load_records
from issuesense.preprocessing import normalize_text


def similar_examples(query: str, records: list[IssueRecord] | None = None, top_k: int = 3) -> list[dict]:
    records = records or load_records()
    corpus = [normalize_text(record.text) for record in records]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    matrix = vectorizer.fit_transform(corpus)
    query_vector = vectorizer.transform([normalize_text(query)])
    scores = cosine_similarity(query_vector, matrix)[0]
    ranked_indexes = scores.argsort()[::-1][:top_k]

    results = []
    for index in ranked_indexes:
        item = asdict(records[index])
        item["similarity"] = float(scores[index])
        results.append(item)
    return results


def build_explanation(query: str, predicted_label: str, confidence: float, top_k: int = 3) -> dict:
    examples = similar_examples(query, top_k=top_k)
    matching = [example for example in examples if example["label"] == predicted_label]
    evidence = matching or examples
    extractive_reason = (
        f"The model predicted {predicted_label} with confidence {confidence:.2f}. "
        f"The nearest labeled examples include {len(matching)} direct label match(es) "
        "among the retrieved evidence."
    )
    llm_reason = maybe_generate_llm_explanation(query, predicted_label, confidence, evidence)
    return {
        "reason": llm_reason or extractive_reason,
        "explanation_provider": "ollama" if llm_reason else "extractive",
        "similar_examples": evidence,
    }


def maybe_generate_llm_explanation(
    query: str,
    predicted_label: str,
    confidence: float,
    evidence: list[dict],
) -> str | None:
    if os.getenv("ISSUESENSE_EXPLANATION_PROVIDER", "extractive") != "ollama":
        return None

    base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b-instruct")
    evidence_text = "\n".join(
        f"- {item['id']} [{item['label']}]: {item['text']}" for item in evidence[:3]
    )
    prompt = (
        "You explain engineering issue classifier outputs. "
        "Use only the input and evidence. Do not invent facts. "
        "If evidence is weak, say human review is needed.\n\n"
        f"Input issue: {query}\n"
        f"Predicted label: {predicted_label}\n"
        f"Confidence: {confidence:.2f}\n"
        f"Evidence:\n{evidence_text}\n\n"
        "Write 2 concise sentences."
    )
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None

    text = str(body.get("response", "")).strip()
    if not is_grounded_llm_explanation(text, predicted_label, evidence):
        return None
    return text


def is_grounded_llm_explanation(text: str, predicted_label: str, evidence: list[dict]) -> bool:
    if len(text.split()) < 10:
        return False
    lowered = text.lower()
    if predicted_label.replace("_", " ") not in lowered and predicted_label not in lowered:
        return False
    evidence_terms = []
    for item in evidence[:3]:
        evidence_terms.extend(normalize_text(item["text"]).split()[:8])
    overlap = sum(1 for term in set(evidence_terms) if len(term) > 3 and term in lowered)
    return overlap >= 2
