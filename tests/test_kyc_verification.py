import pytest
from datetime import datetime
from agents.kyc_agent import KYCAgent
from utils.validators import validate_kyc_verification
from faker import Faker
from utils.audit_logger import AuditLogger

# Initialize Faker with Indian locale
fake = Faker(['en_IN'])

@pytest.fixture
def kyc_agent():
    """Create a KYC agent instance."""
    return KYCAgent(config={
        "model": "gpt-4.5",
        "verification_level": "enhanced",
        "document_check": True,
        "additional_checks": ["ID_proof", "address_proof", "income_proof"],
        "manual_review": True
    })

@pytest.fixture
def test_customer():
    """Create a test customer with Faker."""
    return {
        "name": fake.name(),
        "dob": fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat(),
        "address": f"{fake.street_address()}, {fake.city()}",
        "id_proof": fake.random_number(digits=10),
        "address_proof": fake.random_number(digits=10),
        "income_proof": fake.random_number(digits=10),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "pan": fake.random_uppercase_letter() + fake.random_uppercase_letter() + fake.random_uppercase_letter() + "P" + fake.random_uppercase_letter() + str(fake.random_number(digits=4)) + fake.random_uppercase_letter()
    }

def test_valid_kyc(kyc_agent, test_customer):
    """Test valid KYC verification."""
    result = kyc_agent.verify_customer(test_customer)
    
    # Log the audit event
    audit_logger = AuditLogger()
    audit_logger.log_kyc_verification(
        customer_id=test_customer["pan"],
        decision=result["decision"],
        confidence=result["confidence"]
    )
    
    assert validate_kyc_verification(result)
    assert result["decision"] == "APPROVE"
    assert result["confidence"] > 0.92
    assert "all documents valid" in result["explanation"]
    assert result["action_required"] == False



def test_fake_documents(kyc_agent, test_customer):
    """Test fake documents detection."""
    # Add suspicious patterns
    test_customer["id_proof"] = "FAKE123456789"
    test_customer["address_proof"] = "FAKE123456789"
    
    result = kyc_agent.verify_customer(test_customer)
    
    assert validate_kyc_verification(result)
    assert result["decision"] == "REJECT"
    assert result["confidence"] > 0.9
    assert "suspicious patterns" in result["explanation"]
    assert result["action_required"] == True

def test_demographic_bias(kyc_agent, test_customer):
    """Test demographic bias prevention."""
    # Test across different demographics
    test_cases = [
        {**test_customer, "address": "Mumbai"},
        {**test_customer, "address": "Delhi"},
        {**test_customer, "address": "Chennai"},
        {**test_customer, "address": "Kolkata"}
    ]
    
    results = []
    for case in test_cases:
        result = kyc_agent.verify_customer(case)
        results.append(result["decision"])
    
    # Check for bias
    decision_counts = Counter(results)
    assert max(decision_counts.values()) / len(test_cases) < 0.6  # No single decision > 60%
