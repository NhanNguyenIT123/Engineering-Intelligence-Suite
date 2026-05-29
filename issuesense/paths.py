from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
MODEL_DIR = ROOT_DIR / "models"
OUTPUT_DIR = ROOT_DIR / "outputs"

DATASET_PATH = PROCESSED_DIR / "issues.csv"
BASELINE_MODEL_PATH = MODEL_DIR / "baseline.joblib"
TEXTCNN_MODEL_PATH = MODEL_DIR / "textcnn.pt"
METRICS_PATH = OUTPUT_DIR / "metrics.json"
