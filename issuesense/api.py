from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from issuesense.explain import build_explanation
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
        prediction["explanation"] = build_explanation(
            request.text,
            prediction["label"],
            prediction["confidence"],
        )
        return prediction
    except FileNotFoundError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
