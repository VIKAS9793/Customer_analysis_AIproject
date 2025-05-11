# API Documentation

## Overview
This document provides detailed information about the FinConnectAI system's API endpoints, authentication, request/response formats, and usage guidelines.

## Base URL
```
https://api.finconnect-ai.com/v1
```

## Authentication
All API requests require authentication using an API key in the request header:

```http
Authorization: Bearer YOUR_API_KEY
```

## API Endpoints

### 1. Health Check
Check the system's health status.

```http
GET /health
```

#### Response
```json
{
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": "2025-05-09T15:30:00Z"
}
```

### 2. Customer Analysis
Analyze customer data and generate insights.

```http
POST /analyze
```

#### Request Body
```json
{
    "customer_id": "string",
    "data": {
        "demographics": {
            "age": "number",
            "location": "string",
            "income": "number"
        },
        "behavior": {
            "purchase_history": ["string"],
            "browsing_patterns": ["string"],
            "interaction_frequency": "number"
        }
    }
}
```

#### Response
```json
{
    "analysis_id": "string",
    "customer_id": "string",
    "insights": {
        "segments": ["string"],
        "preferences": {
            "categories": ["string"],
            "price_sensitivity": "number"
        },
        "recommendations": ["string"]
    },
    "confidence_score": "number",
    "timestamp": "string"
}
```

### 3. Batch Analysis
Process multiple customer records in a single request.

```http
POST /analyze/batch
```

#### Request Body
```json
{
    "batch_id": "string",
    "customers": [{
        "customer_id": "string",
        "data": {
            "demographics": {},
            "behavior": {}
        }
    }]
}
```

#### Response
```json
{
    "batch_id": "string",
    "results": [{
        "customer_id": "string",
        "analysis": {}
    }],
    "summary": {
        "total": "number",
        "processed": "number",
        "failed": "number"
    }
}
```

### 4. Model Metrics
Retrieve model performance metrics.

```http
GET /metrics
```

#### Response
```json
{
    "accuracy": "number",
    "precision": "number",
    "recall": "number",
    "f1_score": "number",
    "latency": {
        "p50": "number",
        "p90": "number",
        "p99": "number"
    }
}
```

### 5. Data Processing
Process and validate customer data.

```http
POST /process
```

#### Request Body
```json
{
    "data_type": "string",
    "records": [{
        "id": "string",
        "attributes": {}
    }]
}
```

#### Response
```json
{
    "processed_records": [{
        "id": "string",
        "status": "string",
        "errors": ["string"]
    }]
}
```

## Error Handling

### Error Response Format
```json
{
    "error": {
        "code": "string",
        "message": "string",
        "details": {}
    }
}
```

### Common Error Codes
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `429`: Too Many Requests
- `500`: Internal Server Error

## Rate Limiting
- Default rate limit: 100 requests per minute
- Batch endpoints: 10 requests per minute
- Headers included in response:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`

## Best Practices

### 1. Request Optimization
- Use batch endpoints for multiple records
- Implement retry logic with exponential backoff
- Cache frequently accessed data

### 2. Error Handling
- Implement proper error handling
- Log failed requests
- Monitor error rates

### 3. Security
- Rotate API keys regularly
- Use HTTPS for all requests
- Validate input data

## SDK Examples

### Python
```python
from finconnect_ai import FinConnectAI

# Initialize client
client = FinConnectAI(api_key="YOUR_API_KEY")

# Analyze customer
response = client.analyze_customer(
    customer_id="123",
    data={
        "demographics": {"age": 30},
        "behavior": {"purchases": ["item1", "item2"]}
    }
)

print(response.insights)
```

### JavaScript
```javascript
const FinConnectAI = require('finconnect-ai');

// Initialize client
const client = new FinConnectAI('YOUR_API_KEY');

// Analyze customer
client.analyzeCustomer({
    customerId: '123',
    data: {
        demographics: { age: 30 },
        behavior: { purchases: ['item1', 'item2'] }
    }
})
.then(response => console.log(response.insights))
.catch(error => console.error(error));
```

## Webhook Integration

### 1. Configure Webhook
```http
POST /webhooks/configure
```

#### Request Body
```json
{
    "url": "string",
    "events": ["analysis.complete", "error.detected"],
    "secret": "string"
}
```

### 2. Webhook Payload
```json
{
    "event": "string",
    "timestamp": "string",
    "data": {}
}
```

## Support
For API support or questions:
- Email: api-support@finconnect-ai.com
- Documentation: https://docs.finconnect-ai.com
- Status: https://status.finconnect-ai.com
