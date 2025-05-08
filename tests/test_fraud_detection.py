import pytest
from datetime import datetime, timedelta
from agents.fraud_agent import FraudAgent
from utils.validators import validate_fraud_decision
from utils.data_generator import DataGenerator
from agents.monitoring_agent import MonitoringAgent
from utils.audit_logger import AuditLogger

# Initialize data generator
data_generator = DataGenerator()

@pytest.fixture
def fraud_agent():
    """Create a fraud agent instance."""
    return FraudAgent(config={
        "model": "gpt-4.5",
        "risk_threshold": 0.7,
        "review_required": True
    })

@pytest.fixture
def test_transaction():
    """Create a test transaction using data generator."""
    customer_profile = data_generator.generate_customer_profile()
    return data_generator.generate_transaction(customer_profile)

def test_geo_anomaly_fraud(fraud_agent, test_transaction):
    """Test geographical anomaly detection."""
    # Create a transaction from different location
    test_transaction["location"] = data_generator.generic.address.city()
    test_transaction["customer_location"] = data_generator.generic.address.city()
    
    result = fraud_agent.analyze_transaction(test_transaction)
    
    # Log the audit event
    audit_logger = AuditLogger()
    audit_logger.log_fraud_detection(
        transaction_id=test_transaction["customer_id"],
        decision=result["decision"],
        confidence=result["confidence"]
    )
    
    # Track metrics with monitoring agent
    monitoring_agent = MonitoringAgent(config={
        "alert_thresholds": {
            "error_rate": 0.01,
            "response_time": 2.0,
            "false_positive": 0.05,
            "false_negative": 0.02
        }
    })
    monitoring_agent.track_metric("response_time", 1.5)
    breaches = monitoring_agent.check_thresholds()
    
    assert validate_fraud_decision(result)
    assert result["decision"] == "FLAG"
    assert result["confidence"] > 0.7
    assert "geographical anomaly" in result["explanation"]
    assert result["action_required"] == True
    assert not any(breaches.values())



def test_cryptojacking_detection(fraud_agent, test_transaction):
    """Test cryptojacking detection."""
    # Create a transaction with cryptojacking pattern
    test_transaction["amount"] = 1000
    test_transaction["location"] = "Mining Pool"
    test_transaction["device_id"] = "GPU123"
    
    result = fraud_agent.analyze_transaction(test_transaction)
    
    assert validate_fraud_decision(result)
    assert result["decision"] == "FLAG"
    assert result["confidence"] > 0.8
    assert "cryptojacking" in result["explanation"]
    assert result["action_required"] == True
