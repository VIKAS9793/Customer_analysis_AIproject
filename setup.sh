#!/bin/bash

# Welcome message
echo "Welcome to FinConnectAI Setup Assistant"
echo "==================================="
echo ""

echo "Checking system requirements..."

# Check Python version
python_version=$(python3 --version 2>&1)
if [[ $? -ne 0 ]]; then
    echo "❌ Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Python found: $python_version"

echo ""
echo "Setting up virtual environment..."

# Create and activate virtual environment
python3 -m venv env
source env/bin/activate

echo ""
echo "Installing dependencies..."

# Install dependencies
pip install -r requirements.txt

# Check dependencies
echo ""
echo "Validating dependencies..."
python check_dependencies.py

# Create database
echo ""
echo "Setting up database..."
python -c "from memory.db_manager import DatabaseManager; DatabaseManager()"

echo ""
echo "Setup complete!"
echo ""
echo "To run the system:"
echo "1. Activate the virtual environment: source env/bin/activate"
echo "2. Run the dashboard: streamlit run dashboard/app.py"
echo "3. Run the main application: python main.py"
echo ""
echo "Happy analyzing! 🚀"
