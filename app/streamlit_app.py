import json
import sys
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from issuesense.paths import METRICS_PATH
from issuesense.predict import predict_baseline, predict_textcnn
from issuesense.explain import build_explanation

st.set_page_config(page_title="IssueSense ML", layout="wide")
st.title("IssueSense ML")

sample = "Login API returns HTTP 500 when password contains special characters, but expected HTTP 401."
text = st.text_area("Engineering issue / test-report finding", value=sample, height=140)
model_name = st.selectbox("Model", ["pytorch_textcnn", "tfidf_logistic_regression"])

if st.button("Classify", type="primary"):
    prediction = predict_textcnn(text) if model_name == "pytorch_textcnn" else predict_baseline(text)
    explanation = build_explanation(text, prediction["label"], prediction["confidence"])

    st.metric("Predicted category", prediction["label"])
    st.metric("Confidence", f"{prediction['confidence']:.2f}")
    st.metric("Latency", f"{prediction['latency_ms']:.2f} ms")
    st.write(explanation["reason"])
    st.subheader("Similar labeled examples")
    for example in explanation["similar_examples"]:
        st.markdown(f"**{example['label']}** - `{example['id']}` - similarity `{example['similarity']:.2f}`")
        st.write(example["text"])

if METRICS_PATH.exists():
    st.subheader("Latest Evaluation Metrics")
    st.json(json.loads(METRICS_PATH.read_text(encoding="utf-8")))
