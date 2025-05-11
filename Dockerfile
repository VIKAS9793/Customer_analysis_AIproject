FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY requirements.in .
COPY pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir pip-tools \
    && pip-compile requirements.in --output-file=requirements.txt \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run tests
RUN pytest tests/real_world_tests/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose ports
EXPOSE 8000

# Start the application
CMD ["uvicorn", "finconnect_ai.main:app", "--host", "0.0.0.0", "--port", "8000"]
