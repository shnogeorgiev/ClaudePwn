# ============================================================
# ClaudePwn Windows Setup Script
# Creates venv, installs dependencies, and starts ClaudePwn
# ============================================================

Write-Host "=== ClaudePwn Windows Setup ===" -ForegroundColor Cyan

# Detect project root
$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "Project root: $PROJECT_ROOT"

# Step 1: Create virtual environment if missing
if (!(Test-Path "$PROJECT_ROOT\venv")) {
    Write-Host "[*] Creating virtual environment..."
    python -m venv "$PROJECT_ROOT\venv"
} else {
    Write-Host "[*] venv already exists."
}

# Step 2: Activate venv
Write-Host "[*] Activating virtual environment..."
& "$PROJECT_ROOT\venv\Scripts\Activate.ps1"

# Step 3: Install requirements
Write-Host "[*] Installing requirements..."
pip install --upgrade pip
pip install -r "$PROJECT_ROOT\requirements.txt"

# Step 4: Run ClaudePwn
Write-Host "[*] Starting ClaudePwn..."
python "$PROJECT_ROOT\claudepwn.py"

Write-Host "=== Setup Complete ===" -ForegroundColor Green
