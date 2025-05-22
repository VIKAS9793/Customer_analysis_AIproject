"""
Test suite for FastAPI endpoints and MCP agent routing
"""

import pytest
from fastapi.testclient import TestClient

from app.api_routes import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_transaction():
    return {
        "transaction_id": "tx123",
        "amount": 1000.00,
        "merchant": "Test Store",
        "timestamp": "2025-05-22T13:28:00Z",
        "customer_id": "cust456",
    }


@pytest.fixture
def sample_evaluation_data():
    synthetic_data = [
        {"transaction_id": "1", "is_fraud": True},
        {"transaction_id": "2", "is_fraud": False},
    ]

    model_output = [
        {"transaction_id": "1", "decision": "fraud", "confidence": 0.9},
        {"transaction_id": "2", "decision": "legitimate", "confidence": 0.8},
    ]

    return synthetic_data, model_output


def test_analyze_transaction(client, sample_transaction):
    """Test fraud analysis endpoint."""
    response = client.post("/api/v1/fraud/analyze", json=sample_transaction)
    assert response.status_code == 200

    result = response.json()
    assert "decision" in result
    assert "confidence" in result
    assert "explanation" in result
    assert "recommended_action" in result
    assert "timestamp" in result


def test_evaluate_fraud_detection(client, sample_evaluation_data):
    """Test fraud detection evaluation endpoint."""
    synthetic_data, model_output = sample_evaluation_data

    response = client.post(
        "/api/v1/fraud/evaluate",
        json={"synthetic_data": synthetic_data, "model_output": model_output},
    )
    assert response.status_code == 200

    result = response.json()
    assert "metrics" in result
    assert "metadata" in result
    assert all(
        key in result["metrics"]
        for key in [
            "true_positives",
            "false_positives",
            "true_negatives",
            "false_negatives",
            "precision",
            "recall",
        ]
    )


def test_get_latest_evaluation(client, sample_evaluation_data):
    """Test retrieving latest evaluation report."""
    # First create an evaluation
    synthetic_data, model_output = sample_evaluation_data
    client.post(
        "/api/v1/fraud/evaluate",
        json={"synthetic_data": synthetic_data, "model_output": model_output},
    )

    # Then get latest report
    response = client.get("/api/v1/fraud/latest-report")
    assert response.status_code == 200

    result = response.json()
    assert "metrics" in result
    assert "metadata" in result


def test_invalid_transaction_data(client):
    """Test error handling for invalid transaction data."""
    response = client.post("/api/v1/fraud/analyze", json={})
    assert response.status_code == 400  # Bad request due to missing fields

    error_detail = response.json()["detail"]
    assert "Missing required fields" in error_detail
    assert all(field in error_detail for field in ["transaction_id", "amount", "merchant"])


def test_mismatched_evaluation_data(client):
    """Test error handling for mismatched evaluation data."""
    synthetic_data = [{"is_fraud": True}]
    model_output = []  # Empty output, should cause mismatch

    response = client.post(
        "/api/v1/fraud/evaluate",
        json={"synthetic_data": synthetic_data, "model_output": model_output},
    )
    assert response.status_code == 400  # Bad request due to length mismatch
