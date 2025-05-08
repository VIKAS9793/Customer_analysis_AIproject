# CustomerAI Setup Guide

## Dependencies

### Required Packages
```bash
# Install from requirements.txt
pip install -r requirements.txt

# Required packages:
- openai==1.22.0
- langchain==0.1.17
- streamlit==1.33.0
- spacy==3.7.2
- pandas==2.2.2
- numpy==1.26.4
```

## Installation Steps

1. Clone the repository
2. Install dependencies
3. Set up environment variables
4. Initialize database

### Environment Variables
```bash
# .env file
CUSTOMERAI_API_KEY=your_api_key_here
```

## How to Run

1. Initialize database:
```bash
python setup.sh
```

2. Run the main application:
```bash
python main.py
```

3. Start the dashboard:
```bash
cd dashboard
streamlit run app.py
```

## Troubleshooting

### Common Issues
- API key not found: Check .env file
- Database connection: Verify database path in config.yaml
- Missing dependencies: Run pip install -r requirements.txt

### Error Messages
- "API key not found": Check .env file
- "Database error": Verify database permissions
- "Module not found": Install missing dependencies
