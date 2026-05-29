# IssueSense ML

IssueSense ML is a Python/PyTorch project for classifying engineering issue reports and test-report findings into practical categories such as software defect, requirement gap, test environment issue, data issue, performance issue, and integration issue.

The project is designed for an AI Engineer Intern portfolio: it includes dataset generation, preprocessing, baseline modeling, PyTorch training, evaluation metrics, confusion matrix analysis, and an explanation layer based on similar labeled examples.

## Why This Project

Engineering teams often receive noisy issue reports from testing, QA, APIs, logs, and user workflows. IssueSense ML turns those reports into structured categories so teams can triage faster and explain why a finding was classified a certain way.

This is not an LLM-training project. The classifier is a supervised ML model trained on a synthetic/curated educational dataset, with a lightweight retrieval layer for explanations.

## Labels

- `software_bug`: implementation defect or broken behavior.
- `requirement_gap`: unclear, missing, or conflicting expected behavior.
- `test_environment_issue`: staging, config, network, dependency, or test setup issue.
- `data_issue`: missing, malformed, duplicated, or inconsistent data.
- `performance_issue`: latency, timeout, throughput, or resource usage issue.
- `integration_issue`: service-to-service, API contract, auth, webhook, or third-party integration issue.

## Architecture

```mermaid
flowchart LR
  A["Issue text"] --> B["Preprocessing"]
  B --> C["TF-IDF baseline"]
  B --> D["PyTorch TextCNN"]
  D --> E["Prediction + confidence"]
  B --> F["Similar example retrieval"]
  E --> G["Grounded explanation"]
  F --> G
  C --> H["Metrics"]
  D --> H
```

## Quick Start

Use a Python environment with PyTorch installed. On this machine, the existing DevBrain venv can run the project:

```powershell
cd D:\GITHUB\IssueSense-ML
& D:\GITHUB\DevBrain-AI-Engineering-Intelligence-Platform\.venv\Scripts\python.exe -m issuesense.generate_dataset
& D:\GITHUB\DevBrain-AI-Engineering-Intelligence-Platform\.venv\Scripts\python.exe -m issuesense.train_baseline
& D:\GITHUB\DevBrain-AI-Engineering-Intelligence-Platform\.venv\Scripts\python.exe -m issuesense.train_pytorch
& D:\GITHUB\DevBrain-AI-Engineering-Intelligence-Platform\.venv\Scripts\python.exe -m issuesense.evaluate
```

For a standalone environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m issuesense.generate_dataset
.\.venv\Scripts\python.exe -m issuesense.train_baseline
.\.venv\Scripts\python.exe -m issuesense.train_pytorch
.\.venv\Scripts\python.exe -m issuesense.evaluate
```

## Demo Prediction

```powershell
& D:\GITHUB\DevBrain-AI-Engineering-Intelligence-Platform\.venv\Scripts\python.exe -m issuesense.predict "Login API returns HTTP 500 when password contains special characters, but expected HTTP 401."
```

Optional Streamlit demo:

```powershell
& D:\GITHUB\DevBrain-AI-Engineering-Intelligence-Platform\.venv\Scripts\python.exe -m streamlit run app\streamlit_app.py
```

## Portfolio Claims

Safe CV wording:

- Built a PyTorch-based engineering issue classification system with dataset generation, preprocessing, baseline comparison, model training, and accuracy/F1 evaluation.
- Compared TF-IDF Logistic Regression against a PyTorch TextCNN classifier and documented confusion matrix analysis, latency, and error cases.
- Added a retrieval-based explanation layer that cites similar labeled examples instead of inventing reasons.

Avoid claiming production deployment or training a large language model. This project is a local supervised NLP/ML prototype.
