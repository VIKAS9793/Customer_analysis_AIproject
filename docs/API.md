# FinConnectAI API Documentation

## Overview

FinConnectAI provides a RESTful API for fraud detection and financial analysis. The API is built using FastAPI and follows OpenAPI standards.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All API endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Fraud Detection

#### Analyze Transaction
```http
POST /fraud/analyze
```

Analyzes a transaction for potential fraud in real-time.

**Request Body:**
```json
{
  "transaction_id": "string",
  "amount": "number",
  "currency": "string",
  "merchant": "string",
  "customer_id": "string",
  "location": "string"
}
```

**Response:**
```json
{
  "is_fraudulent": "boolean",
  "confidence_score": "number",
  "explanation": "string",
  "risk_factors": ["string"],
  "timestamp": "string"
}
```

### Currency Exchange

#### Get Exchange Rates
```http
GET /currency/rates/{base_currency}
```

Returns current exchange rates for the specified base currency.

**Parameters:**
- `base_currency` (string): Base currency code (e.g., USD, EUR)

**Response:**
```json
{
  "base_currency": "string",
  "conversion_rates": {
    "currency_code": "number"
  },
  "timestamp": "string",
  "source": "string"
}
```

### Performance Metrics

#### Get Model Performance
```http
GET /metrics/performance
```

Returns current fraud detection model performance metrics.

**Response:**
```json
{
  "accuracy": "number",
  "precision": "number",
  "recall": "number",
  "f1_score": "number",
  "false_positive_rate": "number",
  "false_negative_rate": "number",
  "last_updated": "string"
}
```

## Error Handling

The API uses standard HTTP status codes and returns detailed error messages:

```json
{
  "error": "string",
  "message": "string",
  "status_code": "number",
  "timestamp": "string"
}
```

Common status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

## Rate Limiting

- Standard tier: 100 requests per minute
- Premium tier: 1000 requests per minute

## Best Practices

1. **Caching**
   - Cache exchange rates locally
   - Respect cache-control headers
   - Implement exponential backoff

2. **Error Handling**
   - Implement proper retry logic
   - Handle rate limits gracefully
   - Log all API errors

3. **Security**
   - Keep API keys secure
   - Use HTTPS only
   - Implement request signing

## SDK Examples

### Python
```python
from finconnect import FinConnectClient

client = FinConnectClient(api_key="your_api_key")

# Analyze transaction
result = await client.analyze_transaction(
    transaction_id="tx123",
    amount=1000.00,
    currency="USD",
    merchant="Example Store"
)

# Get exchange rates
rates = await client.get_exchange_rates("USD")
```

### JavaScript
```javascript
const { FinConnectClient } = require('finconnect');

const client = new FinConnectClient('your_api_key');

// Analyze transaction
const result = await client.analyzeTransaction({
  transactionId: 'tx123',
  amount: 1000.00,
  currency: 'USD',
  merchant: 'Example Store'
});
```

## Support

For API support:
- Email: api-support@finconnectai.com
- Documentation: https://docs.finconnectai.com
- Status: https://status.finconnectai.com
