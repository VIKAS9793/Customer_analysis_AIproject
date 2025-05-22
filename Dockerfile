FROM python:3.12-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install only required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ app/
COPY ui/ ui/
COPY connectors/ connectors/
COPY tests/ tests/

# Create necessary directories
RUN mkdir -p logs docs

# Expose ports for FastAPI and Gradio
EXPOSE 8000 7860

# Start both FastAPI and Gradio
CMD ["sh", "scripts/start_demo_env.sh"]
