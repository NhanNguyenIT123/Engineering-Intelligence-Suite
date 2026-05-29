$ErrorActionPreference = "Stop"

$Python = if ($env:ISSUESENSE_PYTHON) {
    $env:ISSUESENSE_PYTHON
} else {
    "D:\GITHUB\DevBrain-AI-Engineering-Intelligence-Platform\.venv\Scripts\python.exe"
}

& $Python -m streamlit run app\streamlit_app.py --server.headless=true --server.address=127.0.0.1 --server.port=8501
