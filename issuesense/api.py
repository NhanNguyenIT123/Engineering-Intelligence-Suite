from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from issuesense.explain import build_explanation
from issuesense.preprocessing import tokenize
from issuesense.predict import predict_baseline, predict_textcnn


class PredictRequest(BaseModel):
    text: str = Field(min_length=8, max_length=4000)
    model: str = "textcnn"


app = FastAPI(title="IssueSense ML API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5176",
        "http://localhost:5176",
        "http://127.0.0.1:5177",
        "http://localhost:5177",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(request: PredictRequest):
    try:
        prediction = predict_baseline(request.text) if request.model == "baseline" else predict_textcnn(request.text)
        explanation = build_explanation(
            request.text,
            prediction["label"],
            prediction["confidence"],
        )
        token_count = len(tokenize(request.text))
        evidence_matches = sum(
            1 for example in explanation["similar_examples"] if example["label"] == prediction["label"]
        )
        prediction["status"] = triage_status(prediction["confidence"], token_count, evidence_matches)
        prediction["review_reasons"] = review_reasons(prediction["confidence"], token_count, evidence_matches)
        prediction["input_quality"] = {
            "token_count": token_count,
            "matching_evidence_count": evidence_matches,
        }
        prediction["explanation"] = explanation
        return prediction
    except FileNotFoundError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


def triage_status(confidence: float, token_count: int, evidence_matches: int) -> str:
    if token_count < 6 or confidence < 0.55 or evidence_matches == 0:
        return "needs_review"
    return "auto_classified"


def review_reasons(confidence: float, token_count: int, evidence_matches: int) -> list[str]:
    reasons = []
    if token_count < 6:
        reasons.append("Input is too short for a reliable engineering issue classification.")
    if confidence < 0.55:
        reasons.append("Model confidence is below the auto-classification threshold.")
    if evidence_matches == 0:
        reasons.append("Retrieved similar examples do not match the predicted label.")
    return reasons
