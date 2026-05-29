from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
CHALLENGE_DIR = DATA_DIR / "challenge"
PROCESSED_DIR = DATA_DIR / "processed"
MODEL_DIR = ROOT_DIR / "models"
OUTPUT_DIR = ROOT_DIR / "outputs"
EXPERIMENT_DIR = OUTPUT_DIR / "experiments"

DATASET_PATH = PROCESSED_DIR / "issues.csv"
CHALLENGE_DATASET_PATH = CHALLENGE_DIR / "issues_challenge.csv"
BASELINE_MODEL_PATH = MODEL_DIR / "baseline.joblib"
TEXTCNN_MODEL_PATH = MODEL_DIR / "textcnn.pt"
METRICS_PATH = OUTPUT_DIR / "metrics.json"
ERROR_ANALYSIS_PATH = OUTPUT_DIR / "error_analysis.md"
EXPERIMENT_LOG_PATH = EXPERIMENT_DIR / "runs.jsonl"
