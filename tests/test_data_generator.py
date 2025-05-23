"""
Tests for the synthetic data generation module.
"""

import os
import tempfile
import pytest
import pandas as pd
from tests.data_generator import TestDataGenerator

def test_data_generator_initialization():
    """Test that the data generator initializes correctly."""
    generator = TestDataGenerator(seed=42)
    assert generator is not None

def test_generate_test_data():
    """Test generating test data."""
    generator = TestDataGenerator(seed=42)
    transactions = generator.generate_test_data(num_transactions=100, fraud_rate=0.1)
    
    assert len(transactions) == 100
    assert all('transaction_id' in t for t in transactions)
    assert all('amount' in t for t in transactions)
    assert all('is_fraud' in t for t in transactions)
    
    # Check that approximately 10% of transactions are fraudulent
    fraud_count = sum(1 for t in transactions if t['is_fraud'])
    assert 5 <= fraud_count <= 15  # Allow some flexibility in the count

def test_generate_model_comparison_data():
    """Test generating data for model comparison."""
    generator = TestDataGenerator(seed=42)
    ground_truth, (model1, model2) = generator.generate_model_comparison_data(
        num_transactions=100,
        fraud_rate=0.1
    )
    
    assert len(ground_truth) == 100
    assert len(model1) == 100
    assert len(model2) == 100
    
    # Verify that model predictions match ground truth
    for tx, pred1, pred2 in zip(ground_truth, model1, model2):
        assert tx["transaction_id"] == pred1["transaction_id"] == pred2["transaction_id"]
        assert pred1["decision"] == ("fraud" if tx["is_fraud"] else "legitimate")
        assert pred2["decision"] == ("fraud" if tx["is_fraud"] else "legitimate")
        assert pred1["confidence"] in [0.1, 0.9]
        assert pred2["confidence"] in [0.05, 0.95]

def test_transaction_amounts():
    """Test that transaction amounts are reasonable."""
    generator = TransactionGenerator(n_customers=10, seed=42)
    transactions = generator.generate_transactions(n_transactions=1000, fraud_rate=0.1)
    
    amounts = [t['amount'] for t in transactions]
    assert all(amount > 0 for amount in amounts)
    assert max(amounts) > 1000  # Some large transactions should exist
    assert min(amounts) < 10  # Some small transactions should exist

def test_fraud_characteristics():
    """Test that fraudulent transactions have expected characteristics."""
    generator = TransactionGenerator(n_customers=10, seed=42)
    transactions = generator.generate_transactions(n_transactions=1000, fraud_rate=0.1)
    
    fraud_transactions = [t for t in transactions if t['is_fraud']]
    legit_transactions = [t for t in transactions if not t['is_fraud']]
    
    # Fraudulent transactions should have a fraud type
    assert all('fraud_type' in t for t in fraud_transactions)
    assert all(t['fraud_type'] is not None for t in fraud_transactions)
    
    # Legitimate transactions should not have a fraud type
    assert all(t.get('fraud_type') is None for t in legit_transactions)
    
    # Fraudulent transactions might have different characteristics
    # (on average, they might be larger, but this is just an example)
    avg_fraud_amount = sum(t['amount'] for t in fraud_transactions) / len(fraud_transactions)
    avg_legit_amount = sum(t['amount'] for t in legit_transactions) / len(legit_transactions)
    
    # This is just an example - in practice, you might have more sophisticated checks
    assert avg_fraud_amount > avg_legit_amount * 0.5  # Fraud is often larger, but not always
