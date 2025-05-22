#!/bin/sh

# Create necessary directories if they don't exist
mkdir -p logs docs

# Start FastAPI server in the background
uvicorn app.api_routes:app --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!

# Start Gradio UI in the background
python ui/gradio_fraud_explain.py &
GRADIO_PID=$!

# Function to handle shutdown
cleanup() {
    echo "Shutting down services..."
    kill $FASTAPI_PID
    kill $GRADIO_PID
    exit 0
}

# Register cleanup function for SIGTERM and SIGINT
trap cleanup SIGTERM SIGINT

# Wait for both processes
wait $FASTAPI_PID $GRADIO_PID
