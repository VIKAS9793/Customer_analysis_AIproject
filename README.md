# FinConnectAI

An AI-powered financial fraud detection and currency exchange system with real-time analysis capabilities.

## Features

### Fraud Detection
- **Real-time Analysis**: Transaction fraud detection using advanced AI
- **Interactive UI**: Gradio-based interface for fraud analysis
- **Explainable AI**: Clear reasoning for fraud decisions

### Currency Services
- **Live Exchange Rates**: Real-time currency conversion
- **Rate Caching**: Efficient rate updates and caching
- **Multi-currency Support**: Major currency pairs supported

### Compliance
- **Regulatory Compliance**: EU AI Act and RBI guidelines
- **Audit Logging**: Comprehensive transaction tracking
- **Documentation**: Automated compliance reporting

### Technical Features
- **FastAPI Backend**: High-performance API endpoints
- **Gradio Frontend**: User-friendly interface
- **Automated Testing**: Comprehensive test coverage
- **Async Support**: Non-blocking operations

## Project Structure

```
├── app/                   # Core application
│   ├── api_routes.py      # FastAPI routes
│   ├── compliance.py      # Compliance management
│   ├── currency_cache.py  # Exchange rate caching
│   ├── currency_exchange.py # Currency conversion
│   ├── fraud_evaluator.py # Fraud evaluation
│   └── models.py         # Data models
├── docs/                  # Documentation
│   ├── API.md            # API documentation
│   ├── ARCHITECTURE.md   # System architecture
│   ├── CONTRIBUTING.md   # Contribution guide
│   ├── SETUP.md         # Setup instructions
│   └── compliance_guidelines.md # Compliance docs
├── tests/                 # Test suite
│   ├── test_api_routes.py  # API tests
│   ├── test_currency_exchange.py # Currency tests
│   └── test_fraud_evaluator.py # Fraud detection tests
└── ui/                    # User interface
    └── gradio_fraud_explain.py # Gradio UI
```

## Demo

Check out our working demo video to see FinConnectAI in action:

[![FinConnectAI Demo](https://img.youtube.com/vi/p3UMmnf9rec/0.jpg)](https://youtu.be/p3UMmnf9rec)

Click the image above to watch the demo on YouTube.

### Demo Features Shown:
- Real-time fraud detection analysis
- Interactive Gradio interface
- Currency conversion functionality
- Transaction risk assessment
- Detailed explanation of fraud decisions

## Quick Start

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Set Environment Variables**
Create `.env` file:
```env
EXCHANGE_RATE_API_KEY=your_api_key_here
```

3. **Run the Application**
```bash
# Start API server
uvicorn app.api_routes:app --reload

# Start Gradio UI
python -m ui.gradio_fraud_explain
```

## API Endpoints

### Fraud Detection
```http
POST /api/v1/fraud/analyze
```
Analyze a transaction for potential fraud.

### Currency Exchange
```http
GET /api/v1/currency/rates/{base_currency}
```
Get current exchange rates for a base currency.

### Compliance
```http
POST /api/v1/compliance/check
```
Verify transaction compliance with regulations.
## Documentation

- [Setup Guide](docs/SETUP.md)
- [API Documentation](docs/API.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Contributing Guidelines](docs/CONTRIBUTING.md)
- [Compliance Guidelines](docs/compliance_guidelines.md)

## Testing

```bash
# Run all tests
pytests tests/

# Run with coverage
pytest --cov=app tests/
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](docs/CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
  - Output: Current model performance statistics

## Getting Started

1. **Installation**
   ```bash
   # Clone the repository
   git clone https://github.com/VIKAS9793/FinConnectAI.git
   cd FinConnectAI

   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Running the Application**
   ```bash
   # Start the FastAPI backend
   python -m uvicorn app.api_routes:app --host 127.0.0.1 --port 8000

   # Start the Gradio UI (in a separate terminal)
   python ui/gradio_fraud_explain.py
   ```

3. **Running Tests**
   ```bash
   pytest
   ```

## Contributing

We welcome contributions! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Copyright (c) 2025 Vikas Sahani. All rights reserved.
