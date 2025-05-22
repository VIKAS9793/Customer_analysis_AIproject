# FinConnectAI

A fraud detection and analysis system with a FastAPI backend and Gradio UI frontend.

## Features

- **Fraud Analysis**: Real-time transaction analysis using the `FraudAgent`
- **Interactive UI**: Gradio-based interface with PWA support for fraud analysis
- **REST API**: FastAPI endpoints for fraud detection and evaluation
- **Authentication**: Role-based access control and consent logging
- **Testing**: Comprehensive test suite for all components

## Project Structure

```
├── agents/                 # AI agents implementation
│   └── fraud_agent.py     # Fraud detection and analysis
├── app/                   # Core application
│   ├── api_routes.py      # FastAPI routes
│   └── fraud_evaluator.py # Fraud evaluation logic
├── auth/                  # Authentication & authorization
│   ├── consent_logger.py  # Consent logging system
│   └── rbac_config.yaml   # Role-based access control config
├── connectors/            # External system connectors
│   └── mock_core_api.py   # Mock core banking API
├── docs/                  # Documentation
│   └── openapi.json       # OpenAPI specification
├── tests/                 # Test suite
│   ├── test_api_routes.py  # API tests
│   ├── test_consent_logger.py # Consent logger tests
│   ├── test_core_banking.py  # Core banking tests
│   └── test_fraud_evaluator.py # Fraud evaluator tests
└── ui/                    # User interface
    └── gradio_fraud_explain.py # Gradio UI for fraud analysis
```

## API Endpoints

- `/api/v1/fraud/analyze`: Analyze a single transaction for fraud
  - Input: Transaction details (ID, amount, merchant, customer)
  - Output: Fraud decision with confidence score and explanation

- `/api/v1/fraud/evaluate`: Evaluate fraud detection performance
  - Input: Ground truth data and model predictions
  - Output: Evaluation metrics (precision, recall, F1, accuracy)

- `/api/v1/fraud/metrics`: Get latest evaluation metrics
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
