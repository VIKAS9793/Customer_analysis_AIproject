# FinConnectAI API Reference

## Core API Functions

### FinConnectAI Class
```python
# Initialize system
def __init__(self, config_path: str = "config.yaml")
    """Initialize the FinConnectAI system.
    
    Args:
        config_path: Path to configuration file
    """

# Process transaction
def process_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]
    """Process a transaction through the system.
    
    Args:
        transaction: Transaction data dictionary
        
    Returns:
        Dict containing transaction result and metadata
    """

# Learn from feedback
def learn_from_feedback(self, feedback: Dict[str, Any]) -> None
    """Process user feedback to improve system performance.
    
    Args:
        feedback: Feedback data dictionary
    """

# Adjust agent thresholds
def adjust_agent_thresholds(self, agent_type: str, new_threshold: float) -> None
    """Adjust thresholds for specific agents.
    
    Args:
        agent_type: Type of agent (fraud, kyc, etc.)
        new_threshold: New threshold value
    """
```

### Core Agents

#### FraudAgent
```python
# Analyze transaction
def analyze_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]
    """Analyze a transaction for potential fraud.
    
    Args:
        transaction: Transaction data to analyze
        
    Returns:
        Dict containing:
        - decision: "FRAUD" or "SAFE"
        - confidence: float between 0 and 1
        - explanation: string explanation
    """
```

#### KYCAgent
```python
# Verify KYC
def verify_kyc(self, data: Dict[str, Any]) -> Dict[str, Any]
    """Verify KYC information.
    
    Args:
        data: KYC verification data dictionary
        
    Returns:
        Dict containing:
        - verified: boolean
        - issues: list of strings (if any)
        - timestamp: string
    """
```

#### ComplianceChecker
```python
# Check compliance
def check_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]
    """Check data for compliance.
    
    Args:
        data: Data to check
        
    Returns:
        Dict containing compliance results
    """

# Get audit trail
def get_audit_trail(self, transaction_id: str) -> Dict[str, Any]
    """Get audit trail for transaction.
    
    Args:
        transaction_id: Transaction identifier
        
    Returns:
        Dict containing audit trail information
    """
```

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
def __init__(self, db_path: str = "finconnectai.db")

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
