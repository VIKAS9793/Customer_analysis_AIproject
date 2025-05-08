# CustomerAI API Reference

## Core API Functions

### CustomerAI Class
```python
# Initialize system
def __init__(self, config_path: str = "config.yaml")

# Process transaction
def process_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]

# Learn from feedback
def learn_from_feedback(self, feedback: Dict[str, Any]) -> None

# Adjust agent thresholds
def adjust_agent_thresholds(self, agent_type: str, new_threshold: float) -> None
```

### Agents

#### FraudAgent
```python
# Analyze transaction
def analyze_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]

# Calculate risk score
def _calculate_risk_score(self, transaction: Dict[str, Any]) -> float

# Make decision
def _make_decision(self, risk_score: float) -> str
```

#### KYCAgent
```python
# Verify customer
def verify_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]

# Perform document checks
def _verify_documents(self, customer_data: Dict[str, Any]) -> Dict[str, bool]

# Calculate confidence
def _calculate_confidence(self, doc_verification: Dict[str, bool]) -> float
```

### Memory System

#### DatabaseManager
```python
# Initialize database
def __init__(self, db_path: str = "customerai.db")

# Store decision
def store_decision(self, decision_data: Dict[str, Any]) -> None

# Get decision
def get_decision(self, decision_id: str) -> Dict[str, Any]

# Store feedback
def store_feedback(self, feedback_data: Dict[str, Any]) -> None
```

## Response Formats

### Decision Response
```json
{
    "decision": string,  // APPROVE/REJECT/FLAG/ERROR
    "confidence": float,
    "explanation": string,
    "recommended_action": string,
    "timestamp": string
}
```

### Feedback Response
```json
{
    "feedback_id": string,
    "status": string,  // SUCCESS/ERROR
    "message": string
}
```

## Error Handling

### Common Errors
- `APIError`: API key issues
- `DatabaseError`: Database connection
- `ValidationError`: Invalid input
- `ConfigurationError`: Invalid config

### Error Responses
```json
{
    "error": {
        "code": string,
        "message": string,
        "timestamp": string
    }
}
```
