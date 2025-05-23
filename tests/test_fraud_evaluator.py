"""Tests for the fraud detection evaluation module."""

from datetime import datetime, timedelta, timezone
import random
from pathlib import Path
from typing import Dict, Any
import pytest

from app.fraud_evaluator import FraudEvaluator

# Use standard library timezone
UTC = timezone.utc

# Helper function to create UTC timestamp
def create_utc_timestamp(minutes_offset: int) -> str:
    """Create a UTC timestamp with specified minutes offset."""
    # Get current time in local timezone
    now = datetime.now()
    # Convert to UTC
    utc_time = now.astimezone(UTC)
    # Subtract offset and return ISO format
    return (utc_time - timedelta(minutes=minutes_offset)).isoformat()

from pathlib import Path
from typing import Dict, Any
import random

import pytest

from app.fraud_evaluator import FraudEvaluator


@pytest.fixture
def evaluator(tmp_path):
    return FraudEvaluator(output_dir=str(tmp_path))


@pytest.fixture
def sample_data():
    synthetic_data = [
        {"transaction_id": "1", "is_fraud": True},
        {"transaction_id": "2", "is_fraud": False},
        {"transaction_id": "3", "is_fraud": True},
        {"transaction_id": "4", "is_fraud": False},
    ]

    model_output = [
        {"transaction_id": "1", "decision": "fraud", "confidence": 0.9},
        {"transaction_id": "2", "decision": "legitimate", "confidence": 0.8},
        {"transaction_id": "3", "decision": "legitimate", "confidence": 0.6},
        {"transaction_id": "4", "decision": "fraud", "confidence": 0.7},
    ]

    return synthetic_data, model_output


def test_evaluation_metrics(evaluator, sample_data):
    synthetic_data, model_output = sample_data
    report = evaluator.evaluate_predictions(synthetic_data, model_output)

    metrics = report["metrics"]
    assert metrics["true_positives"] == 1
    assert metrics["false_positives"] == 1
    assert metrics["true_negatives"] == 1
    assert metrics["false_negatives"] == 1
    assert metrics["precision"] == 0.5
    assert metrics["recall"] == 0.5
    assert metrics["accuracy"] == 0.5


def test_report_generation(evaluator, sample_data):
    synthetic_data, model_output = sample_data
    evaluator.evaluate_predictions(synthetic_data, model_output)

    # Check if report file was created
    reports = list(Path(evaluator.output_dir).glob("eval_report_*.json"))
    assert len(reports) == 1

    # Verify latest report retrieval
    latest = evaluator.get_latest_report()
    assert "metrics" in latest
    assert "metadata" in latest


def generate_fraud_transaction(transaction_id: str, fraud_type: str) -> Dict[str, Any]:
    """Generate a fraudulent transaction of specific type."""
    base = {
        "transaction_id": transaction_id,
        "amount": random.uniform(10, 10000),
        "timestamp": create_utc_timestamp(random.randint(1, 1440)),
        "currency": random.choice(["USD", "EUR", "GBP"]),
        "merchant_category": random.choice(
            ["electronics", "travel", "retail", "services"]
        ),
        "is_fraud": True,
        "fraud_type": fraud_type
    }
    
    if fraud_type == "unauthorized":
        base.update({
            "card_present": False,
            "ip_country_mismatch": True,
            "device_id_changed": True
        })
    elif fraud_type == "account_takeover":
        base.update({
            "multiple_failed_logins": random.randint(3, 10),
            "password_change_recent": True,
            "unusual_login_location": True
        })
    elif fraud_type == "cnp_fraud":
        base.update({
            "card_present": False,
            "billing_shipping_mismatch": True,
            "high_risk_country": True
        })
    
    return base


def generate_legitimate_transaction(transaction_id: str) -> Dict[str, Any]:
    """Generate a legitimate transaction."""
    return {
        "transaction_id": transaction_id,
        "amount": random.uniform(1, 500),
        "timestamp": create_utc_timestamp(random.randint(1, 1440)),
        "currency": random.choice(["USD", "EUR", "GBP"]),
        "merchant_category": random.choice(
            ["groceries", "dining", "transport", "utilities"]
        ),
        "is_fraud": False,
        "card_present": random.choice([True, False]),
        "ip_country_match": True,
        "device_id_consistent": True
    }


def test_unauthorized_transaction_detection(evaluator, tmp_path):
    """Test detection of unauthorized transactions."""
    # Generate test data
    test_data = [generate_legitimate_transaction(str(i)) for i in range(5)]
    fraud = generate_fraud_transaction("fraud_1", "unauthorized")
    test_data.append(fraud)
    
    # Model output (simulate perfect detection for this test)
    model_output = [
        {"transaction_id": tx["transaction_id"], 
         "decision": "fraud" if tx.get("transaction_id") == "fraud_1" else "legitimate",
         "confidence": 0.95 if tx.get("transaction_id") == "fraud_1" else 0.1}
        for tx in test_data
    ]
    
    # Evaluate
    report = evaluator.evaluate_predictions(test_data, model_output)
    assert report["metrics"]["true_positives"] == 1
    assert report["metrics"]["false_negatives"] == 0


def test_account_takeover_detection(evaluator, tmp_path):
    """Test detection of account takeover attempts."""
    # Generate test data with account takeover pattern
    test_data = [generate_legitimate_transaction(str(i)) for i in range(5)]
    takeover = generate_fraud_transaction("takeover_1", "account_takeover")
    test_data.append(takeover)
    
    # Model output (simulate perfect detection for this test)
    model_output = [
        {"transaction_id": tx["transaction_id"], 
         "decision": "fraud" if tx.get("transaction_id") == "takeover_1" else "legitimate",
         "confidence": 0.93 if tx.get("transaction_id") == "takeover_1" else 0.1}
        for tx in test_data
    ]
    
    # Evaluate
    report = evaluator.evaluate_predictions(test_data, model_output)
    assert report["metrics"]["true_positives"] == 1
    assert report["metrics"]["false_positives"] == 0


def test_cnp_fraud_detection(evaluator, tmp_path):
    """Test detection of Card Not Present (CNP) fraud."""
    # Generate test data with CNP fraud pattern
    test_data = [generate_legitimate_transaction(str(i)) for i in range(5)]
    cnp_fraud = generate_fraud_transaction("cnp_1", "cnp_fraud")
    test_data.append(cnp_fraud)
    
    # Model output (simulate perfect detection for this test)
    model_output = [
        {"transaction_id": tx["transaction_id"], 
         "decision": "fraud" if tx.get("transaction_id") == "cnp_1" else "legitimate",
         "confidence": 0.97 if tx.get("transaction_id") == "cnp_1" else 0.1}
        for tx in test_data
    ]
    
    # Evaluate
    report = evaluator.evaluate_predictions(test_data, model_output)
    assert report["metrics"]["true_positives"] == 1
    assert report["metrics"]["false_negatives"] == 0


def test_edge_case_high_value_legitimate(evaluator, tmp_path):
    """Test that high-value legitimate transactions are not flagged as fraud."""
    # Generate high-value but legitimate transaction (e.g., travel purchase)
    legit_high_value = generate_legitimate_transaction("high_value_1")
    legit_high_value["amount"] = 5000  # High value
    legit_high_value["merchant_category"] = "travel"  # Common for high value
    legit_high_value["is_fraud"] = False
    
    test_data = [generate_legitimate_transaction(str(i)) for i in range(5)]
    test_data.append(legit_high_value)
    
    # Model should correctly identify as legitimate
    model_output = [
        {"transaction_id": tx["transaction_id"], 
         "decision": "legitimate",
         "confidence": 0.9}
        for tx in test_data
    ]
    
    # Evaluate
    report = evaluator.evaluate_predictions(test_data, model_output)
    assert report["metrics"]["false_positives"] == 0
    assert report["metrics"]["true_negatives"] == len(test_data)


def test_high_volume_velocity(evaluator, tmp_path):
    """Test detection under high volume and velocity conditions."""
    # Generate large volume of transactions with varying timestamps
    test_data = []
    for i in range(1000):  # Simulate high volume
        # Create transactions with timestamps spread over 1 hour
        minutes_offset = random.randint(0, 60)
        transaction = {
            "transaction_id": f"tx_{i}",
            "amount": random.uniform(1, 1000),
            "timestamp": create_utc_timestamp(minutes_offset),
            "currency": random.choice(["USD", "EUR", "GBP"]),
            "merchant_category": random.choice([
                "groceries", "dining", "transport", "utilities",
                "electronics", "travel", "retail", "services"
            ]),
            "is_fraud": False if i < 950 else True,  # 5% fraud rate
            "card_present": random.choice([True, False]),
            "ip_country_match": True,
            "device_id_consistent": True
        }
        test_data.append(transaction)
    
    # Add some fraudulent transactions with rapid succession
    fraud_times = [0, 1, 2]  # Three frauds within 2 minutes
    for i, minutes in enumerate(fraud_times):
        fraud = {
            "transaction_id": f"fraud_{i}",
            "amount": random.uniform(1000, 5000),
            "timestamp": create_utc_timestamp(minutes),
            "currency": random.choice(["USD", "EUR", "GBP"]),
            "merchant_category": random.choice(["electronics", "travel"]),
            "is_fraud": True,
            "card_present": False,
            "ip_country_match": False,
            "device_id_consistent": False
        }
        test_data.append(fraud)
    
    # Model output (simulate detection)
    model_output = [
        {
            "transaction_id": tx["transaction_id"],
            "decision": "fraud" if tx.get("is_fraud") else "legitimate",
            "confidence": 0.95 if tx.get("is_fraud") else 0.1
        }
        for tx in test_data
    ]
    
    # Evaluate
    report = evaluator.evaluate_predictions(test_data, model_output)
    
    # Check metrics
    assert report["metrics"]["true_positives"] >= 3  # At least 3 frauds detected
    assert report["metrics"]["false_positives"] <= 50  # Acceptable false positive rate
    assert report["metrics"]["precision"] >= 0.85  # High precision expected
    assert report["metrics"]["recall"] >= 0.90  # High recall expected


def test_identity_theft_detection(evaluator, tmp_path):
    """Test detection of identity theft patterns."""
    # Generate test data with identity theft pattern
    test_data = [generate_legitimate_transaction(str(i)) for i in range(10)]
    
    # Add identity theft pattern: New account with unusual spending pattern
    identity_theft = generate_fraud_transaction("id_theft_1", "identity_theft")
    identity_theft.update({
        "new_account": True,
        "unusual_spending_pattern": True,
        "multiple_locations_short_time": True,
        "unusual_payment_methods": True
    })
    test_data.append(identity_theft)
    
    # Model output (simulate detection of identity theft)
    model_output = [
        {
            "transaction_id": tx["transaction_id"],
            "decision": "fraud" if tx.get("transaction_id") == "id_theft_1" else "legitimate",
            "confidence": 0.92 if tx.get("transaction_id") == "id_theft_1" else 0.1
        }
        for tx in test_data
    ]
    
    # Evaluate
    report = evaluator.evaluate_predictions(test_data, model_output)
    assert report["metrics"]["true_positives"] == 1
    assert report["metrics"]["false_negatives"] == 0


def test_adversarial_examples(evaluator, tmp_path):
    """Test detection of adversarial examples with subtle fraudulent modifications."""
    # Generate legitimate-looking but actually fraudulent transactions
    test_data = []
    
    # Adversarial example 1: Slightly modified legitimate-looking transaction
    adv1 = generate_legitimate_transaction("adv_1")
    adv1.update({
        "is_fraud": True,
        "amount": 999,  # Just below common fraud threshold
        "transaction_time": "03:00:00",  # Unusual time
        "ip_address": "192.168.1.1",  # Common IP but with other suspicious factors
        "device_id": "device_" + "1"*32  # Suspicious device ID pattern
    })
    test_data.append(adv1)
    
    # Adversarial example 2: Transaction with manipulated features
    adv2 = generate_legitimate_transaction("adv_2")
    adv2.update({
        "is_fraud": True,
        "billing_zip": "12345",  # Common zip but mismatched with IP location
        "shipping_zip": "67890",  # Different from billing
        "email_domain": "tempmail.com"  # Disposable email
    })
    test_data.append(adv2)
    
    # Add some legitimate transactions
    test_data.extend([generate_legitimate_transaction(f"legit_{i}") for i in range(5)])
    
    # Model should detect the adversarial patterns
    model_output = [
        {
            "transaction_id": tx["transaction_id"],
            "decision": "fraud" if tx.get("is_fraud") else "legitimate",
            "confidence": 0.88 if tx.get("is_fraud") else 0.9
        }
        for tx in test_data
    ]
    
    # Evaluate
    report = evaluator.evaluate_predictions(test_data, model_output)
    assert report["metrics"]["true_positives"] == 2  # Should catch both adversarial examples


def test_high_volume_velocity(evaluator, tmp_path):
    """Test system behavior under high volume and velocity conditions."""
    # Generate a large number of transactions in a short time
    num_transactions = 1000
    test_data = []
    
    # Generate mixed legitimate and fraudulent transactions
    for i in range(num_transactions):
        if i % 20 == 0:  # 5% fraud rate
            fraud_type = random.choice(["unauthorized", "account_takeover", "cnp_fraud"])
            tx = generate_fraud_transaction(f"fraud_{i}", fraud_type)
        else:
            tx = generate_legitimate_transaction(f"legit_{i}")
        test_data.append(tx)
    
    # Simulate model processing with some realistic delay
    model_output = []
    for tx in test_data:
        is_fraud = tx.get("is_fraud", False)
        # Simulate model confidence based on fraud type and features
        confidence = random.uniform(0.85, 0.98) if is_fraud else random.uniform(0.7, 0.95)
        model_output.append({
            "transaction_id": tx["transaction_id"],
            "decision": "fraud" if is_fraud else "legitimate",
            "confidence": confidence,
            "processing_time_ms": random.randint(5, 50)  # Simulate processing time
        })
    
    # Evaluate performance under load
    start_time = datetime.now(timezone.utc)
    report = evaluator.evaluate_predictions(test_data, model_output)
    processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
    
    # Assert system handles load within acceptable time
    assert processing_time < 5.0  # Should process 1000 transactions in under 5 seconds
    
    # Verify metrics are reasonable
    expected_frauds = sum(1 for tx in test_data if tx.get("is_fraud"))
    assert report["metrics"]["true_positives"] > 0
    assert report["metrics"]["false_positives"] < expected_frauds * 0.1  # <10% FP rate
    
    # Verify system maintains performance characteristics
    avg_processing_time = sum(tx.get("processing_time_ms", 0) for tx in model_output) / len(model_output)
    assert avg_processing_time < 100  # Average processing time < 100ms per transaction
