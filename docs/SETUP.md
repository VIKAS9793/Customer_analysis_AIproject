# FinConnectAI Setup Guide

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Git

## Installation

1. **Clone the Repository**
```bash
git clone https://github.com/VIKAS9793/FinConnectAI.git
cd FinConnectAI
```

2. **Set Up Virtual Environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
Copy `.env.example` to `.env` and update with your settings:
```
EXCHANGE_RATE_API_KEY=your_api_key_here
DATABASE_URL=your_db_url
```

## Development Setup

1. **Install Development Dependencies**
```bash
pip install -r test-requirements.txt
```

2. **Run Tests**
```bash
pytest tests/
```

3. **Start Development Server**
```bash
uvicorn app.api_routes:app --reload
```

4. **Launch Gradio UI**
```bash
python -m ui.gradio_fraud_explain
```

## Configuration

### API Keys
- Exchange Rate API: Sign up at [exchangerate-api.com](https://www.exchangerate-api.com/)
- Other API keys as needed

### Database Setup
1. Create a PostgreSQL database
2. Update DATABASE_URL in .env
3. Run migrations: `alembic upgrade head`

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_fraud_evaluator.py

# Run with coverage
pytest --cov=app tests/
```

### Test Configuration
- Update `tests/conftest.py` for test fixtures
- Mock API responses in `tests/mocks/`

## Deployment

### Docker Deployment
```bash
# Build image
docker build -t finconnectai .

# Run container
docker run -p 8000:8000 finconnectai
```

### Production Configuration
1. Update `config/production.yaml`
2. Set secure environment variables
3. Configure logging in `config/logging.yaml`

## Troubleshooting

### Common Issues

1. **AsyncClient Initialization Error**
   - Ensure proper event loop handling
   - Check async context management

2. **Database Connection Issues**
   - Verify DATABASE_URL format
   - Check database server status
   - Confirm network connectivity

3. **API Rate Limits**
   - Monitor exchange rate API usage
   - Implement proper caching
   - Handle rate limit errors

### Getting Help
- Open an issue on GitHub
- Check existing issues and documentation
- Contact maintainers
