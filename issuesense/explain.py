from dataclasses import asdict

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
    reason = (
        f"The model predicted {predicted_label} with confidence {confidence:.2f}. "
        f"The nearest labeled examples include {len(matching)} direct label match(es) "
        "among the retrieved evidence."
    )
    return {"reason": reason, "similar_examples": evidence}
