.PHONY: install test lint format check-codestyle typecheck clean

# Installation
install:
	pip install -e .
	pip install -r requirements-dev.txt
	pre-commit install

# Testing
test:
	python -m pytest tests/ -v --cov=app --cov-report=term-missing

test-cov:
	python -m pytest tests/ -v --cov=app --cov-report=html

# Linting and formatting
lint:
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
