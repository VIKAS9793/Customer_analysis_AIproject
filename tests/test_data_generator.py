"""
Tests for the synthetic data generation module.
"""

import os
import tempfile
import pytest
import pandas as pd
from app.data_generator import TransactionGenerator, generate_synthetic_dataset

def test_transaction_generator_initialization():
    """Test that the transaction generator initializes correctly."""
    generator = TransactionGenerator(n_customers=10, seed=42)
    assert len(generator.customer_profiles) == 10
    assert all('customer_id' in customer for customer in generator.customer_profiles)
    assert all('account_balance' in customer for customer in generator.customer_profiles)

def test_generate_transactions():
    """Test generating a small number of transactions."""
    generator = TransactionGenerator(n_customers=10, seed=42)
    transactions = generator.generate_transactions(n_transactions=100, fraud_rate=0.1)
    
    assert len(transactions) == 100
    assert all('transaction_id' in t for t in transactions)
    assert all('amount' in t for t in transactions)
    assert all('is_fraud' in t for t in transactions)
    
    # Check that approximately 10% of transactions are fraudulent
    fraud_count = sum(1 for t in transactions if t['is_fraud'])
    assert 5 <= fraud_count <= 15  # Allow some flexibility in the count

def test_generate_synthetic_dataset():
    """Test generating and saving a synthetic dataset."""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
        try:
            # Generate a small test dataset
            df = generate_synthetic_dataset(
                n_transactions=100,
                fraud_rate=0.1,
                output_file=tmp.name
            )
            
            # Check that the file was created and has the right columns
            assert os.path.exists(tmp.name)
            assert not df.empty
            assert 'transaction_id' in df.columns
            assert 'customer_id' in df.columns
            assert 'amount' in df.columns
            assert 'is_fraud' in df.columns
            
            # Check that the fraud rate is approximately correct
            fraud_rate = df['is_fraud'].mean()
            assert 0.05 <= fraud_rate <= 0.15  # Allow some flexibility
            
        finally:
            # Clean up
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

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
