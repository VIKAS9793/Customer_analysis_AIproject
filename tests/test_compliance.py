import pytest
from datetime import datetime
from agents.compliance_agent import ComplianceAgent
from utils.validators import validate_compliance_check

@pytest.fixture
def compliance_agent():
    """Create a compliance agent instance."""
    return ComplianceAgent(config={
        "model": "gpt-4.5",
        "regulatory_framework": ["RBI", "SEBI", "DPDP Act", "GDPR"],
        "audit_frequency": "daily",
        "review_required": True
    })

@pytest.fixture
def test_transaction():
    """Create a test transaction."""
    return {
        "amount": 5000,
        "location": "Mumbai",
        "customer_id": "CUST123456",
        "timestamp": datetime.utcnow().isoformat()
    }

def test_insider_trading(compliance_agent, test_transaction):
    """Test insider trading detection."""
    # Create insider trading scenario
    test_transaction["insider_id"] = "INSIDER123"
    test_transaction["company_code"] = "INDUSIND"
    
    result = compliance_agent.check_insider_trading(test_transaction)
    
    assert validate_compliance_check(result)
    assert result["compliance_status"] == "REJECTED"
    assert result["risk_level"] == "HIGH"
    assert result["action_required"] == True
    assert "insider trading" in result["analysis"]

def test_aml_pattern(compliance_agent, test_transaction):
    """Test AML pattern detection."""
    # Create AML pattern
    test_transaction["amount"] = 100000
    test_transaction["location"] = "Cayman Islands"
    test_transaction["beneficiary"] = "Shell Company"
    
    result = compliance_agent.check_aml_patterns(test_transaction)
    
    assert validate_compliance_check(result)
    assert result["compliance_status"] == "FLAGGED"
    assert result["risk_level"] == "HIGH"
    assert result["action_required"] == True
    assert "AML pattern" in result["analysis"]

def test_kyc_compliance(compliance_agent, test_customer):
    """Test KYC compliance."""
    # Create KYC compliance check
    result = compliance_agent.check_kyc_compliance(test_customer)
    
    assert validate_compliance_check(result)
    assert result["compliance_status"] == "APPROVED"
    assert result["risk_level"] == "LOW"
    assert result["action_required"] == False
    assert "KYC compliant" in result["analysis"]

def test_data_privacy(compliance_agent, test_data):
    """Test data privacy compliance."""
    # Create data privacy check
    result = compliance_agent.check_data_privacy(test_data)
    
    assert validate_compliance_check(result)
    assert result["compliance_status"] == "APPROVED"
    assert result["risk_level"] == "LOW"
    assert result["action_required"] == False
    assert "data privacy compliant" in result["analysis"]

def test_regulatory_reporting(compliance_agent, test_transaction):
    """Test regulatory reporting."""
    # Create regulatory reporting check
    result = compliance_agent.generate_regulatory_report(test_transaction)
    
    assert validate_compliance_check(result)
    assert result["report_generated"] == True
    assert result["compliance_status"] == "APPROVED"
    assert result["action_required"] == False
    assert "regulatory report" in result["analysis"]
