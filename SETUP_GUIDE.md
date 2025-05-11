# FinConnectAI Setup Guide

⚠️ **IMPORTANT DISCLAIMER** ⚠️

This setup guide is provided as a foundation for business adaptation. Businesses MUST:

1. **Customize Configuration**
   - All configuration values must be set according to your organization's requirements
   - Default values shown in this guide are for demonstration purposes only

2. **Security Requirements**
   - Hardware and software requirements must meet your organization's security standards
   - All security configurations must be reviewed and adjusted

3. **Compliance Requirements**
   - All system settings must comply with your organization's regulations
   - Data retention and processing must follow your compliance policies

---

## System Requirements
- Python 3.10 or higher
- Minimum 4GB RAM
- Minimum 1GB disk space for dependencies

## Installation

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import finconnectai" && echo "Installation successful"
```

### 2. Configuration

#### Environment Variables
Create a `.env` file in the project root:
```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Security Settings
SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-encryption-key

# Monitoring Configuration
PROMETHEUS_PORT=9090
GRAFANA_API_KEY=your-grafana-key

# Database Settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=customer_analysis
DB_USER=your-db-user
DB_PASSWORD=your-db-password
```

### 3. Database Setup
```bash
# Initialize database
alembic upgrade head

# Verify database connection
python -c "from finconnectai.db import verify_connection; verify_connection()"
```

### 4. Security Configuration
```bash
# Generate encryption keys
python scripts/generate_keys.py

# Configure security policies
python scripts/configure_security.py
```

### 5. Monitoring Setup

#### Prometheus
```bash
# Start Prometheus server
docker-compose up -d prometheus

# Verify metrics endpoint
curl http://localhost:9090/metrics
```

#### Grafana
```bash
# Start Grafana
docker-compose up -d grafana

# Import dashboards
python scripts/import_dashboards.py
```

## Verification

### 1. Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=finconnectai
```

### 2. Start Services
```bash
# Start API server
uvicorn main:app --reload

# Start monitoring
python -m finconnectai.monitoring.start
```

### 3. Verify Components

#### Security Checks
```bash
# Run security audit
python scripts/security_audit.py

# Test KYC verification
python scripts/test_kyc.py
```

#### Fraud Detection
```bash
# Test fraud detection
python scripts/test_fraud.py

# Run anomaly detection
python scripts/test_anomalies.py
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify PostgreSQL is running
   - Check database credentials in `.env`
   - Ensure database exists

2. **Monitoring Setup Issues**
   - Check if Prometheus/Grafana containers are running
   - Verify ports are not in use
   - Check firewall settings

3. **Security Configuration**
   - Regenerate encryption keys
   - Verify file permissions
   - Check security policy configuration

### Support

For additional support:
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Submit an issue on GitHub
- Contact the development team

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
FINCONNECTAI_API_KEY=your_api_key_here
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
