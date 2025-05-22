# fix_lint_issues.ps1
# Run this from PowerShell: ./fix_lint_issues.ps1

Write-Host "Installing necessary packages..."
pip install black autoflake isort

Write-Host "Running black to auto-format code..."
python -m black app agents ui tests auth --line-length 100

Write-Host "Running autoflake to remove unused imports and variables..."
python -m autoflake --in-place --remove-all-unused-imports --remove-unused-variables -r app agents ui tests auth

Write-Host "Sorting imports with isort (optional)..."
python -m isort app agents ui tests auth

Write-Host "Rechecking with flake8..."
python -m flake8 app agents ui tests auth --max-line-length=100

Write-Host "Done fixing lint issues."
