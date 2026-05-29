$ErrorActionPreference = "Stop"

$Python = if ($env:ISSUESENSE_PYTHON) {
    $env:ISSUESENSE_PYTHON
} else {
    "D:\GITHUB\DevBrain-AI-Engineering-Intelligence-Platform\.venv\Scripts\python.exe"
}

& $Python -m uvicorn issuesense.api:app --host 127.0.0.1 --port 8765
