# Check if Python 3.11 is installed
$python311Path = (Get-Command python3.11 -ErrorAction SilentlyContinue).Path

if (-not $python311Path) {
    Write-Host "Python 3.11 is not installed. Please install it from python.org"
    Write-Host "Download URL: https://www.python.org/downloads/release/python-3118/"
    exit 1
}

Write-Host "Python 3.11 found at: $python311Path"

# Create virtual environment
Write-Host "Creating virtual environment with Python 3.11..."
if (Test-Path "venv") {
    Remove-Item -Recurse -Force "venv"
}

& $python311Path -m venv venv

# Activate virtual environment and install dependencies
Write-Host "Activating virtual environment and installing dependencies..."
.\venv\Scripts\Activate.ps1

python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

Write-Host "Environment setup complete!"
