import pytest
from datetime import datetime
from agents.security_agent import SecurityAgent
from utils.validators import validate_security_check
from faker import Faker
from utils.audit_logger import AuditLogger

# Initialize Faker with Indian locale
fake = Faker(['en_IN'])

@pytest.fixture
def security_agent():
    """Create a security agent instance."""
    return SecurityAgent(config={
        "model": "gpt-4.5",
        "encryption_enabled": True,
        "pii_masking": True,
        "audit_enabled": True
    })

@pytest.fixture
def test_data():
    """Create test data with Faker."""
    return {
        "name": fake.name(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "ssn": fake.random_number(digits=9),
        "password": fake.password(length=12)
    }

def test_pii_masking(security_agent, test_data):
    """Test PII masking."""
    masked_data = security_agent.mask_pii(test_data)
    
    # Log the audit event
    audit_logger = AuditLogger()
    audit_logger.log_security_event(
        "PII_MASKING",
        {
            "status": "SUCCESS",
            "masked_fields": list(test_data.keys())
        }
    )
    
    assert validate_security_check(masked_data)
    assert test_data["name"] not in str(masked_data)
    assert test_data["phone"] not in str(masked_data)
    assert test_data["email"] not in str(masked_data)
    assert str(test_data["ssn"]) not in str(masked_data)
    assert test_data["password"] not in str(masked_data)

def test_encryption(security_agent, test_data):
    """Test encryption."""
    sensitive_data = {
        "ssn": "123-45-6789",
        "password": "securepassword123"
    }
    
    encrypted = security_agent.encrypt(sensitive_data)
    decrypted = security_agent.decrypt(encrypted)
    
    assert validate_security_check(encrypted)
    assert encrypted != sensitive_data
    assert decrypted == sensitive_data

def test_deepfake_detection(security_agent):
    """Test deepfake detection."""
    voice_sample = "deepfake_voice.wav"
    
    result = security_agent.detect_deepfake(voice_sample)
    
    assert validate_security_check(result)
    assert result["risk_level"] == "HIGH"
    assert result["action_required"] == True
    assert "deepfake" in result["analysis"]

def test_phishing_detection(security_agent):
    """Test phishing detection."""
    email_content = "Dear customer, please verify your account details..."
    
    result = security_agent.detect_phishing(email_content)
    
    assert validate_security_check(result)
    assert result["risk_level"] == "HIGH"
    assert result["action_required"] == True
    assert "suspicious" in result["analysis"]

def test_cryptojacking_detection(security_agent):
    """Test cryptojacking detection."""
    system_metrics = {
        "cpu_usage": 95,
        "gpu_usage": 90,
        "memory_usage": 80,
        "processes": ["miner.exe", "gpu_miner.exe"]
    }
    
    result = security_agent.detect_cryptojacking(system_metrics)
    
    assert validate_security_check(result)
    assert result["risk_level"] == "HIGH"
    assert result["action_required"] == True
    assert "cryptojacking" in result["analysis"]
