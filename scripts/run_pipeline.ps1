$ErrorActionPreference = "Stop"

$Python = if ($env:ISSUESENSE_PYTHON) {
    $env:ISSUESENSE_PYTHON
} else {
    "D:\GITHUB\DevBrain-AI-Engineering-Intelligence-Platform\.venv\Scripts\python.exe"
}

Write-Host "Using Python: $Python"

& $Python -m issuesense.generate_dataset
& $Python -m issuesense.train_baseline
& $Python -m issuesense.train_pytorch
& $Python -m issuesense.evaluate
& $Python -m unittest discover -s tests

Write-Host "Pipeline completed."
