"""Tests for the fraud detection evaluation module."""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timezone
import pytest
from pytest import approx as pytest_approx
import random

from app.fraud_evaluator import FraudEvaluator
from tests.test_utils import (
    generate_test_data,
    generate_fraud_transaction,
    generate_legitimate_transaction,
    create_utc_timestamp
)

# Fixtures for common test data patterns
@pytest.fixture
def fraud_transaction():
    return generate_fraud_transaction("test_fraud", "unauthorized")

@pytest.fixture
def legitimate_transaction():
    return generate_legitimate_transaction("test_legit")

@pytest.fixture
def mixed_transaction_data():
    return generate_test_data(num_transactions=10, fraud_rate=0.2)

@pytest.fixture
def model_output_factory():
    def _factory(transactions, fraud_confidence=0.9, legit_confidence=0.1):
        return [
            {"transaction_id": tx["transaction_id"], 
             "decision": "fraud" if tx["is_fraud"] else "legitimate",
             "confidence": fraud_confidence if tx["is_fraud"] else legit_confidence}
            for tx in transactions
        ]
    return _factory

@pytest.fixture
def evaluator(tmp_path):
    return FraudEvaluator(output_dir=str(tmp_path))

@pytest.fixture
def sample_data(mixed_transaction_data, model_output_factory):
    # Use fixture for test data and create model output
    test_data = mixed_transaction_data
    model_output = model_output_factory(
        test_data,
        fraud_confidence=0.9,
        legit_confidence=0.8
    )
    return test_data, model_output

def test_evaluation_metrics(evaluator, sample_data):
    """Test evaluation metrics calculation."""
    test_data, model_output = sample_data
    
    # Evaluate
    report = evaluator.evaluate_predictions(test_data, model_output)
    metrics = report["metrics"]
    
    # Verify basic metrics
    assert metrics["true_positives"] >= 0
    assert metrics["false_positives"] >= 0
    assert metrics["true_negatives"] >= 0
    assert metrics["false_negatives"] >= 0
    
    # Verify rates
    assert 0 <= metrics["precision"] <= 1
    assert 0 <= metrics["recall"] <= 1
    assert 0 <= metrics["f1_score"] <= 1
    assert 0 <= metrics["accuracy"] <= 1
    
    # Verify business metrics
    assert 0 <= metrics["fraud_rate"] <= 1
    assert 0 <= metrics["fraud_capture_rate"] <= 1
    assert 0 <= metrics["false_positive_rate"] <= 1
    assert 0 <= metrics["false_negative_rate"] <= 1
    
    # Verify monetary metrics
    assert metrics["total_fraud_amount"] >= 0
    assert metrics["missed_fraud_amount"] >= 0
    assert 0 <= metrics["fraud_loss_rate"] <= 1
    
    # Verify confidence metrics
    assert 0 <= metrics["fraud_confidence_avg"] <= 1
    assert metrics["fraud_confidence_std"] >= 0
    assert 0 <= metrics["legitimate_confidence_avg"] <= 1
    assert metrics["legitimate_confidence_std"] >= 0
    
    # Verify AUC metrics
    assert 0 <= metrics["auc_pr"] <= 1
    assert 0 <= metrics["auc_roc"] <= 1
    
    # Verify metadata
    assert "metadata" in report
    assert "total_samples" in report["metadata"]
    assert "timestamp" in report["metadata"]
    assert isinstance(report["metadata"]["timestamp"], str)


def test_auc_metrics(evaluator, sample_data):
    """Test AUC metrics calculation."""
    test_data, model_output = sample_data
    
    # Create test data with varying confidence scores
    num_samples = len(test_data)
    fraud_indices = [i for i, tx in enumerate(test_data) if tx["is_fraud"]]
    
    # Create model output with varying confidence scores
    model_output = [
        {
            "transaction_id": tx["transaction_id"],
            "decision": "fraud" if tx["is_fraud"] else "legitimate",
            "confidence": 0.9 if tx["is_fraud"] else 0.1
        }
        for tx in test_data
    ]
    
    # Evaluate
    report = evaluator.evaluate_predictions(test_data, model_output)
    metrics = report["metrics"]
    
    # Verify AUC metrics
    assert "auc_pr" in metrics
    assert "auc_roc" in metrics
    assert 0 <= metrics["auc_pr"] <= 1
    assert 0 <= metrics["auc_roc"] <= 1
    
    # For perfect separation, AUC should be close to 1
    assert metrics["auc_pr"] > 0.8
    assert metrics["auc_roc"] > 0.8


@pytest.fixture
def evaluator(tmp_path):
    return FraudEvaluator(output_dir=str(tmp_path))


@pytest.fixture
def sample_data(mixed_transaction_data, model_output_factory):
    # Use fixture for test data and create model output
    test_data = mixed_transaction_data
    model_output = model_output_factory(
        test_data,
        fraud_confidence=0.9,
        legit_confidence=0.8
    )
    return test_data, model_output

def test_evaluation_metrics(evaluator, sample_data):
    """Test evaluation metrics calculation."""
    test_data, model_output = sample_data
    
    # Evaluate
    report = evaluator.evaluate_predictions(test_data, model_output)
    metrics = report["metrics"]
    
    # Verify basic metrics
    assert metrics["true_positives"] >= 0
    assert metrics["false_positives"] >= 0
    assert metrics["true_negatives"] >= 0
    assert metrics["false_negatives"] >= 0
    
    # Verify rates
    assert 0 <= metrics["precision"] <= 1
    assert 0 <= metrics["recall"] <= 1
    assert 0 <= metrics["f1_score"] <= 1
    assert 0 <= metrics["accuracy"] <= 1
    
    # Verify business metrics
    assert 0 <= metrics["fraud_rate"] <= 1
    assert 0 <= metrics["fraud_capture_rate"] <= 1
    assert 0 <= metrics["false_positive_rate"] <= 1
    assert 0 <= metrics["false_negative_rate"] <= 1
    
    # Verify monetary metrics
    assert metrics["total_fraud_amount"] >= 0
    assert metrics["missed_fraud_amount"] >= 0
    assert 0 <= metrics["fraud_loss_rate"] <= 1
    
    # Verify confidence metrics
    assert 0 <= metrics["fraud_confidence_avg"] <= 1
    assert metrics["fraud_confidence_std"] >= 0
    assert 0 <= metrics["legitimate_confidence_avg"] <= 1
    assert metrics["legitimate_confidence_std"] >= 0
    
    # Verify AUC metrics
    assert 0 <= metrics["auc_pr"] <= 1
    assert 0 <= metrics["auc_roc"] <= 1
    
    # Verify metadata
    assert "metadata" in report
    assert "total_samples" in report["metadata"]
    assert "timestamp" in report["metadata"]
    assert isinstance(report["metadata"]["timestamp"], str)


def test_auc_metrics(evaluator, sample_data):
    """Test AUC metrics calculation."""
    test_data, model_output = sample_data
    
    # Create test data with varying confidence scores
    num_samples = len(test_data)
    fraud_indices = [i for i, tx in enumerate(test_data) if tx["is_fraud"]]
    
    # Create model output with varying confidence scores
    model_output = [
        {
            "transaction_id": tx["transaction_id"],
            "decision": "fraud" if tx["is_fraud"] else "legitimate",
            "confidence": 0.9 if tx["is_fraud"] else 0.1
        }
        for tx in test_data
    ]
    
    # Evaluate
    report = evaluator.evaluate_predictions(test_data, model_output)
    metrics = report["metrics"]
    
    # Verify AUC metrics
    assert "auc_pr" in metrics
    assert "auc_roc" in metrics
    assert 0 <= metrics["auc_pr"] <= 1
    assert 0 <= metrics["auc_roc"] <= 1
    
    # For perfect separation, AUC should be close to 1
    assert metrics["auc_pr"] > 0.8
    assert metrics["auc_roc"] > 0.8


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


def test_unauthorized_transaction_detection(evaluator, fraud_transaction, model_output_factory):
    """Test detection of unauthorized transactions."""
    # Create test data with one unauthorized fraud
    test_data = [
        generate_legitimate_transaction(
            f"legit_{i}",
            amount=100,
            timestamp_offset=720,
            currency="USD",
            merchant_category="groceries",
            card_present=True
        )
        for i in range(5)
    ]
    test_data.append(fraud_transaction)
    
    # Create model output with perfect detection
    model_output = model_output_factory(
        test_data,
        fraud_confidence=0.95,
        legit_confidence=0.1
    )
    
    # Evaluate
    report = evaluator.evaluate_predictions(test_data, model_output)
    metrics = report["metrics"]
    assert metrics["true_positives"] == 1
    assert metrics["false_negatives"] == 0
    assert metrics["false_positives"] == 0
    assert metrics["accuracy"] > 0.9


def test_account_takeover_detection(evaluator, fraud_transaction, model_output_factory):
    """Test detection of account takeover attempts."""
    # Create test data with one account takeover fraud
    test_data = [
        generate_legitimate_transaction(
            f"legit_{i}",
            amount=100,
            timestamp_offset=720,
            currency="USD",
            merchant_category="groceries",
            card_present=True
        )
        for i in range(5)
    ]
    
    # Update fraud transaction to be account takeover
    takeover = fraud_transaction.copy()
    takeover["transaction_id"] = "takeover_1"
    takeover["fraud_type"] = "account_takeover"
    takeover.update({
        "multiple_failed_logins": 7,
        "password_change_recent": True,
        "unusual_login_location": True
    })
    test_data.append(takeover)
    
    # Create model output with perfect detection
    model_output = model_output_factory(
        test_data,
        fraud_confidence=0.93,
        legit_confidence=0.1
    )
    
    # Evaluate
    report = evaluator.evaluate_predictions(test_data, model_output)
    metrics = report["metrics"]
    assert metrics["true_positives"] == 1
    assert metrics["false_negatives"] == 0
    assert metrics["false_positives"] == 0
    assert metrics["accuracy"] > 0.9


def test_cnp_fraud_detection(evaluator, fraud_transaction, model_output_factory):
    """Test detection of card-not-present fraud."""
    # Create test data with only legitimate transactions
    test_data = [
        generate_legitimate_transaction(
            f"legit_{i}",
            amount=100,
            timestamp_offset=720,
            currency="USD",
            merchant_category="groceries",
            card_present=True
        )
        for i in range(5)
    ]
    
    # Add single CNP fraud transaction
    cnp = fraud_transaction.copy()
    cnp["transaction_id"] = "cnp_1"
    cnp["fraud_type"] = "cnp"
    cnp.update({
        "card_present": False,
        "ip_country_match": False,
        "device_id_consistent": False,
        "amount": 500
    })
    test_data.append(cnp)
    
    # Model output (simulate perfect detection for this test)
    model_output = [
        {"transaction_id": tx["transaction_id"], 
         "decision": "fraud" if tx.get("transaction_id") == "cnp_1" else "legitimate",
         "confidence": 0.97 if tx.get("transaction_id") == "cnp_1" else 0.1}
        for tx in test_data
    ]
    
    # Evaluate
    report = evaluator.evaluate_predictions(test_data, model_output)
    metrics = report["metrics"]
    assert metrics["true_positives"] == 1
    assert metrics["false_negatives"] == 0
    assert metrics["false_positives"] == 0
    assert metrics["accuracy"] > 0.9


def test_edge_case_high_value_legitimate(evaluator, tmp_path):
    """Test that high-value legitimate transactions are not flagged as fraud."""
    # Generate test data with one high-value legitimate transaction
    test_data = generate_test_data(num_transactions=5, fraud_rate=0)
    
    # Add high-value legitimate transaction
    high_value = generate_legitimate_transaction("high_value_1")
    high_value["amount"] = 5000  # High value
    high_value["merchant_category"] = "travel"  # Common for high value
    test_data.append(high_value)
    
    # Model output (should not flag high-value legitimate)
    model_output = [
        {"transaction_id": tx["transaction_id"], 
         "decision": "legitimate",
         "confidence": 0.95}
        for tx in test_data
    ]
    
    # Evaluate
    report = evaluator.evaluate_predictions(test_data, model_output)
    metrics = report["metrics"]
    
    # Verify metrics
    assert metrics["false_positives"] == 0
    assert metrics["false_positive_rate"] == 0
    assert metrics["legitimate_confidence_avg"] > 0.9
    assert metrics["total_fraud_amount"] == 0
    assert metrics["missed_fraud_amount"] == 0


def test_business_metrics(evaluator, tmp_path):
    """Test business-oriented metrics calculation."""
    # Create test data with various fraud patterns
    test_data = [
        generate_fraud_transaction("fraud_1", "unauthorized"),
        generate_fraud_transaction("fraud_2", "account_takeover"),
        generate_legitimate_transaction("legit_1"),
        generate_legitimate_transaction("legit_2")
    ]
    
    # Model output with some misses
    model_output = [
        {"transaction_id": "fraud_1", "decision": "fraud", "confidence": 0.9},
        {"transaction_id": "fraud_2", "decision": "legitimate", "confidence": 0.3},
        {"transaction_id": "legit_1", "decision": "legitimate", "confidence": 0.9},
        {"transaction_id": "legit_2", "decision": "legitimate", "confidence": 0.8}
    ]
    
    # Evaluate
    report = evaluator.evaluate_predictions(test_data, model_output)
    metrics = report["metrics"]
    
    # Verify business metrics
    assert metrics["fraud_rate"] == 0.5  # 2/4 transactions are fraud
    assert metrics["fraud_capture_rate"] == 0.5  # Captured 1 out of 2 frauds
    assert metrics["false_positive_rate"] == 0  # No false positives
    assert metrics["false_negative_rate"] == 0.5  # Missed 1 out of 2 frauds
    assert metrics["fraud_loss_rate"] > 0  # Should have some missed fraud amount


def test_auc_metrics(evaluator, tmp_path):
    """Test AUC-PR and AUC-ROC calculations."""
    # Create test data with varying confidence scores
    test_data = [
        generate_fraud_transaction("fraud_1", "unauthorized"),
        generate_fraud_transaction("fraud_2", "account_takeover"),
        generate_legitimate_transaction("legit_1"),
        generate_legitimate_transaction("legit_2")
    ]
    
    # Model output with varying confidences
    model_output = [
        {"transaction_id": "fraud_1", "decision": "fraud", "confidence": 0.9},
        {"transaction_id": "fraud_2", "decision": "fraud", "confidence": 0.8},
        {"transaction_id": "legit_1", "decision": "legitimate", "confidence": 0.1},
        {"transaction_id": "legit_2", "decision": "legitimate", "confidence": 0.2}
    ]
    
    # Evaluate
    report = evaluator.evaluate_predictions(test_data, model_output)
    metrics = report["metrics"]
    
    # Verify AUC metrics
    assert metrics["auc_pr"] > 0.7  # Should be good since high confidence for fraud
    assert metrics["auc_roc"] > 0.7  # Should be good since good separation


def test_confidence_metrics(evaluator, tmp_path):
    """Test confidence score statistics."""
    # Create test data with varying confidence scores
    test_data = [
        generate_fraud_transaction("fraud_1", "unauthorized"),
        generate_fraud_transaction("fraud_2", "account_takeover"),
        generate_legitimate_transaction("legit_1"),
        generate_legitimate_transaction("legit_2")
    ]
    
    # Model output with varying confidences
    model_output = [
        {"transaction_id": "fraud_1", "decision": "fraud", "confidence": 0.95},
        {"transaction_id": "fraud_2", "decision": "fraud", "confidence": 0.9},
        {"transaction_id": "legit_1", "decision": "legitimate", "confidence": 0.1},
        {"transaction_id": "legit_2", "decision": "legitimate", "confidence": 0.15}
    ]
    
    # Evaluate
    report = evaluator.evaluate_predictions(test_data, model_output)
    metrics = report["metrics"]
    
    # Verify confidence metrics
    assert metrics["fraud_confidence_avg"] > 0.9  # High confidence for fraud
    assert metrics["legitimate_confidence_avg"] < 0.2  # Low confidence for legitimate
    assert metrics["fraud_confidence_std"] < 0.1  # Low variance in fraud confidences
    assert metrics["legitimate_confidence_std"] < 0.1  # Low variance in legitimate confidences


def test_edge_case_no_fraud(evaluator, sample_data):
    """Test evaluation when there are no fraud cases."""
    test_data, model_output = sample_data
    
    # Generate only legitimate transactions
    test_data = [generate_legitimate_transaction(str(i)) for i in range(10)]
    
    # Model output (should be all legitimate)
    model_output = [
        {"transaction_id": tx["transaction_id"], 
         "decision": "legitimate",
         "confidence": 0.95}
        for tx in test_data
    ]
    
    # Evaluate
    report = evaluator.evaluate_predictions(test_data, model_output)
    metrics = report["metrics"]
    
    # Verify metrics
    assert metrics["fraud_rate"] == 0
    assert metrics["fraud_capture_rate"] == 0
    assert metrics["false_positive_rate"] == 0
    assert metrics["false_negative_rate"] == 0
    assert metrics["true_positives"] == 0
    assert metrics["false_positives"] == 0
    assert metrics["true_negatives"] == len(test_data)
    assert metrics["false_negatives"] == 0
    assert metrics["accuracy"] == 1.0


def test_high_volume_velocity(evaluator, tmp_path):
    """Test detection under high volume and velocity conditions."""
    # Generate large volume of transactions with varying timestamps
    test_data = []
    for i in range(1000):  # Simulate high volume
        # Create transactions with timestamps spread over 1 hour
        minutes_offset = i % 60  # Use fixed pattern instead of random
        transaction = {
            "transaction_id": f"tx_{i}",
            "amount": 500,  # Fixed amount
            "timestamp": create_utc_timestamp(minutes_offset),
            "currency": "USD",  # Fixed currency
            "merchant_category": "groceries" if i % 2 == 0 else "electronics",  # Alternating categories
            "is_fraud": False if i < 950 else True,  # 5% fraud rate
            "card_present": True,  # Fixed value
            "ip_country_match": True,
            "device_id_consistent": True
        }
        test_data.append(transaction)
    
    # Add some fraudulent transactions with rapid succession
    fraud_times = [0, 1, 2]  # Three frauds within 2 minutes
    fraud_amounts = []
    for i, minutes in enumerate(fraud_times):
        amount = 2500  # Fixed amount for fraud
        fraud = {
            "transaction_id": f"fraud_{i}",
            "amount": amount,
            "timestamp": create_utc_timestamp(minutes),
            "currency": "USD",
            "merchant_category": "electronics",
            "is_fraud": True,
            "card_present": False,
            "ip_country_match": False,
            "device_id_consistent": False
        }
        fraud_amounts.append(amount)
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
    metrics = report["metrics"]
    
    # Check basic metrics
    assert metrics["true_positives"] == 53  # 50 regular fraud + 3 rapid succession
    assert metrics["false_positives"] == 0  # No false positives in this test
    assert metrics["precision"] == 1.0  # Perfect precision
    assert metrics["recall"] == 1.0  # Perfect recall
    
    # Check business metrics
    assert metrics["fraud_rate"] == pytest_approx(0.053, abs=0.001)  # 53/1003 fraud rate
    assert metrics["fraud_capture_rate"] == 1.0  # Perfect capture
    assert metrics["false_positive_rate"] == 0  # No false positives
    assert metrics["false_negative_rate"] == 0  # No false negatives
    
    # Check monetary metrics
    total_fraud = sum(fraud_amounts) + (50 * 500)  # 3 rapid fraud + 50 regular fraud
    assert metrics["total_fraud_amount"] == total_fraud
    assert metrics["missed_fraud_amount"] == 0  # No missed fraud in this test
    assert metrics["fraud_loss_rate"] == 0  # No loss in this test
    
    # Check confidence metrics
    assert metrics["fraud_confidence_avg"] >= 0.90  # High confidence for fraud
    assert metrics["legitimate_confidence_avg"] <= 0.2  # Low confidence for legitimate
    
    # Check AUC metrics
    assert metrics["auc_pr"] >= 0.90  # High AUC-PR expected
    
    # Check metadata
    assert report["metadata"]["total_samples"] == len(test_data)
    assert report["metadata"]["fraud_cases"] == 53  # 50 random + 3 rapid frauds
    assert report["metadata"]["legitimate_cases"] == 947  # 950 - 3 rapid frauds


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


if __name__ == "__main__":
    pytest.main(["-v", "--no-header", __file__])
