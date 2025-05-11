# FinConnectAI Database Schema

## Tables

### Decisions Table
```sql
CREATE TABLE decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_type TEXT NOT NULL,
    decision TEXT NOT NULL CHECK (decision IN ('APPROVE', 'REJECT', 'FLAG', 'ERROR')),
    confidence REAL CHECK (confidence BETWEEN 0 AND 1),
    explanation TEXT,
    action_taken TEXT,
    timestamp TEXT,
    reviewer_id TEXT,
    status TEXT DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED', 'FLAGGED'))
);
```

### Feedback Table
```sql
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id INTEGER,
    reviewer_id TEXT NOT NULL,
    feedback_type TEXT NOT NULL CHECK (feedback_type IN ('human_override', 'system_error', 'clarification')),
    feedback_text TEXT NOT NULL,
    action_taken TEXT,
    timestamp TEXT,
    FOREIGN KEY (decision_id) REFERENCES decisions (id)
);
```

## Data Retention

### Decision Records
- Retention: 365 days
- Automatic deletion
- Audit trail
- Documentation

### Feedback Records
- Retention: 90 days
- Regular deletion
- Compliance requirement
- Security monitoring

## Security Measures

### Access Control
- Role-based access
- API key authentication
- Token management
- Audit trail

### Encryption
- AES-256 encryption
- Secure key management
- Regular key rotation
- Hardware security modules

## Audit Logging

### Required Fields
- Decision ID
- Timestamp
- Reviewer ID
- Action taken
- Status

### Format
```json
{
    "action_taken": string,
    "timestamp": string,
    "reviewer_id": string,
    "decision": string,
    "status": string
}
```
