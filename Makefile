.PHONY: init install lint format mypy test test-async doc clean docker

# Initialize project environment
init:
	conda create -n finconnectai python=3.9 -y
	conda activate finconnectai
	pip install "poetry>=1.6.0"
	poetry install

# Install project in development mode
install:
	poetry install

# Run code formatting and linting
lint:
	black .
	isort .
	mypy app/
	flake8 .
	black --check .
	isort --check-only .

format:
	black .
	isort .

# Type checking
typecheck:
	mypy .

# Clean up
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type f -name "*.py[co]" -delete
	find . -type d -name ".coverage" -exec rm -r {} +
	find . -type d -name "htmlcov" -exec rm -r {} +
	find . -type d -name ".ipynb_checkpoints" -exec rm -r {} +

# Development server
dev:
	uvicorn app.main:app --reload

# Build documentation
docs:
	cd docs && make html

# Run all checks
check: lint typecheck test
