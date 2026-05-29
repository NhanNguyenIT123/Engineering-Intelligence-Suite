import json
import sys
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from issuesense.explain import build_explanation
from issuesense.labels import LABEL_DESCRIPTIONS
from issuesense.paths import METRICS_PATH
from issuesense.predict import predict_baseline, predict_textcnn

st.set_page_config(page_title="IssueSense ML", page_icon=":bar_chart:", layout="wide")

st.markdown(
    """
    <style>
      .main {
        background: linear-gradient(180deg, #f7f9fc 0%, #ffffff 34%);
      }
      .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
      }
      .hero {
        padding: 1.5rem 1.6rem;
        border: 1px solid #d9e2ef;
        border-radius: 10px;
        background: linear-gradient(135deg, #ffffff 0%, #eef5ff 100%);
        box-shadow: 0 16px 38px rgba(32, 54, 91, 0.08);
        margin-bottom: 1rem;
      }
      .hero h1 {
        font-size: 2.2rem;
        margin: 0 0 .3rem 0;
        color: #102033;
        letter-spacing: 0;
      }
      .hero p {
        color: #40536b;
        margin: 0;
        font-size: 1rem;
      }
      .metric-card {
        border: 1px solid #dce5f2;
        border-radius: 8px;
        padding: 1rem;
        background: #ffffff;
        min-height: 112px;
        box-shadow: 0 8px 22px rgba(32, 54, 91, 0.06);
        transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
      }
      .metric-card:hover {
        transform: translateY(-2px);
        border-color: #b8c9e4;
        box-shadow: 0 14px 30px rgba(32, 54, 91, 0.10);
      }
      .metric-label {
        color: #65758b;
        font-size: .82rem;
        text-transform: uppercase;
        font-weight: 700;
      }
      .metric-value {
        color: #102033;
        font-size: 1.5rem;
        font-weight: 800;
        margin-top: .35rem;
      }
      .evidence {
        border-left: 4px solid #276ef1;
        background: #f8fbff;
        padding: .8rem 1rem;
        border-radius: 6px;
        margin-bottom: .7rem;
        transition: transform .18s ease, background .18s ease;
      }
      .evidence:hover {
        transform: translateX(3px);
        background: #f1f7ff;
      }
      .badge {
        display: inline-block;
        padding: .2rem .5rem;
        border-radius: 999px;
        background: #e8f0ff;
        color: #194c9f;
        font-weight: 700;
        font-size: .78rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_metrics() -> dict | None:
    if not METRICS_PATH.exists():
        return None
    return json.loads(METRICS_PATH.read_text(encoding="utf-8"))


def metric_card(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div class="hero">
      <h1>IssueSense ML</h1>
      <p>Engineering issue classification with PyTorch, baseline comparison, challenge-set evaluation, and grounded example-based explanations.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

sample = "Login API returns HTTP 500 when password contains special characters, but expected HTTP 401."

with st.sidebar:
    st.header("Model Controls")
    model_name = st.radio("Classifier", ["pytorch_textcnn", "tfidf_logistic_regression"], index=0)
    st.caption("PyTorch TextCNN is the portfolio model. TF-IDF Logistic Regression is the baseline.")
    st.divider()
    st.subheader("Labels")
    for label, description in LABEL_DESCRIPTIONS.items():
        st.markdown(f"**{label}**")
        st.caption(description)

metrics = load_metrics()
tabs = st.tabs(["Classify", "Evaluation", "Error Analysis", "Project Notes"])

with tabs[0]:
    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        text = st.text_area("Engineering issue / test-report finding", value=sample, height=170)
        run = st.button("Classify issue", type="primary", use_container_width=True)
    with right:
        st.subheader("Demo Scenarios")
        examples = [
            "The ERP connector sends customerId but the CRM endpoint now expects customer_id.",
            "The export endpoint takes 18 seconds for 20 thousand rows and frequently hits the gateway timeout.",
            "The story says managers can override the limit, but it does not define the approval threshold.",
        ]
        for example in examples:
            st.code(example, language="text")

    if run:
        prediction = predict_textcnn(text) if model_name == "pytorch_textcnn" else predict_baseline(text)
        explanation = build_explanation(text, prediction["label"], prediction["confidence"])

        col1, col2, col3 = st.columns(3)
        with col1:
            metric_card("Predicted category", prediction["label"])
        with col2:
            metric_card("Confidence", f"{prediction['confidence']:.2f}")
        with col3:
            metric_card("Latency", f"{prediction['latency_ms']:.2f} ms")

        st.markdown("### Grounded Explanation")
        st.info(explanation["reason"])
        st.markdown("### Similar Labeled Evidence")
        for example in explanation["similar_examples"]:
            st.markdown(
                f"""
                <div class="evidence">
                  <span class="badge">{example['label']}</span>
                  <strong>{example['id']}</strong> · similarity {example['similarity']:.2f}
                  <p>{example['text']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

with tabs[1]:
    st.subheader("Evaluation Summary")
    if not metrics:
        st.warning("Run `python -m issuesense.evaluate` to generate metrics.")
    else:
        dataset = metrics["dataset"]
        challenge = metrics["challenge_dataset"]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            metric_card("Training records", str(dataset["train_records"]))
        with col2:
            metric_card("Synthetic test", str(dataset["test_records"]))
        with col3:
            metric_card("Challenge records", str(challenge["total_records"]))
        with col4:
            metric_card("Labels", str(len(dataset["label_distribution"])))

        for split in metrics["evaluation_splits"]:
            st.markdown(f"### {split['name']}")
            rows = []
            for model in split["models"]:
                rows.append(
                    {
                        "model": model["model"],
                        "accuracy": round(model["accuracy"], 3),
                        "macro_f1": round(model["macro_f1"], 3),
                        "avg_latency_ms": round(model["avg_latency_ms"], 3),
                    }
                )
            st.table(rows)
            with st.expander(f"Confusion matrices for {split['name']}"):
                for model in split["models"]:
                    st.markdown(f"**{model['model']}**")
                    st.json(model["confusion_matrix"])

with tabs[2]:
    st.subheader("Error Analysis")
    if not metrics:
        st.warning("Run evaluation first.")
    else:
        for split in metrics["evaluation_splits"]:
            st.markdown(f"### {split['name']}")
            for model_name, errors in split["error_analysis"].items():
                st.markdown(f"**{model_name}**")
                if not errors:
                    st.success("No misclassifications in this split.")
                for error in errors:
                    st.error(f"{error['id']}: expected {error['expected']}, predicted {error['predicted']}")
                    st.write(error["text"])

with tabs[3]:
    st.subheader("Portfolio Positioning")
    st.write(
        "IssueSense ML demonstrates a complete AI/ML workflow: dataset creation, preprocessing, "
        "baseline comparison, PyTorch training, evaluation, error analysis, and interpretable prediction."
    )
    st.markdown(
        """
        **Honest claim:** local supervised NLP/ML prototype for engineering issue triage.

        **Do not claim:** production deployment, enterprise data access, or training a large language model.
        """
    )
