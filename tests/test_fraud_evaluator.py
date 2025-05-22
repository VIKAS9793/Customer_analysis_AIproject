"""
Tests for the fraud detection evaluation module
"""

from pathlib import Path

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
