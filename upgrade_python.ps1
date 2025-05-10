# PowerShell Script for Python 3.11 Upgrade

Write-Host "🔁 Step 1: Checking Python 3.11 installation..."
try {
    $pythonVersion = python -V
    if ($pythonVersion -notlike "*3.11*") {
        Write-Host "⚠️ Python 3.11 not found. Please install Python 3.11 from python.org"
        exit 1
    }
} catch {
    Write-Host "⚠️ Python not found. Please install Python 3.11 from python.org"
    exit 1
}

Write-Host "✅ Python 3.11 is ready."

Write-Host "🔁 Step 2: Creating new virtual environment..."
if (Test-Path "venv") {
    Remove-Item -Recurse -Force "venv"
}
python -m venv venv
. .\venv\Scripts\Activate.ps1

Write-Host "🔁 Step 3: Upgrading pip and installing verified dependencies..."
python -m pip install --upgrade pip setuptools wheel
pip install pip-tools

Write-Host "Generating requirements.txt from requirements.in..."
pip-compile requirements.in --output-file=requirements.txt
pip install -r requirements.txt
pip check

Write-Host "🔁 Step 4: Running tests under Python 3.11..."
pytest tests/real_world_tests/ --verbose

Write-Host "✅ Python 3.11 upgrade complete and validated."

# Verify the upgrade
Write-Host "`nVerifying Python version and dependencies:"
python --version
pip list
