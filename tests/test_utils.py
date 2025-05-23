"""
Test utilities and fixtures for FinConnectAI fraud detection tests
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Any
import random
from pathlib import Path

# Set random seed for reproducibility
random.seed(42)

# Use standard library timezone
UTC = timezone.utc


def create_utc_timestamp(minutes_offset: int) -> str:
    """Create a UTC timestamp with specified minutes offset."""
    # Get current time in UTC
    utc_time = datetime.now(UTC) + timedelta(minutes=minutes_offset)
    return utc_time.isoformat()


def generate_fraud_transaction(transaction_id: str, fraud_type: str, amount: float = 1000, timestamp_offset: int = 720, currency: str = "USD", merchant_category: str = "electronics") -> Dict[str, Any]:
    """Generate a fraudulent transaction of specific type."""
    base = {
        "transaction_id": transaction_id,
        "amount": amount,
        "timestamp": create_utc_timestamp(timestamp_offset),
        "currency": currency,
        "merchant_category": merchant_category,
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


def generate_legitimate_transaction(transaction_id: str, amount: float = 100, timestamp_offset: int = 720, currency: str = "USD", merchant_category: str = "groceries", card_present: bool = True) -> Dict[str, Any]:
    """Generate a legitimate transaction."""
    return {
        "transaction_id": transaction_id,
        "amount": amount,
        "timestamp": create_utc_timestamp(timestamp_offset),
        "currency": currency,
        "merchant_category": merchant_category,
        "is_fraud": False,
        "card_present": card_present,
        "ip_country_match": True,
        "device_id_consistent": True
    }


def generate_test_data(num_transactions: int = 10, fraud_rate: float = 0.1) -> list:
    """Generate test data with specified number of transactions and fraud rate."""
    transactions = []
    fraud_types = ["unauthorized", "account_takeover", "cnp_fraud"]
    for i in range(num_transactions):
        if i < num_transactions * fraud_rate:
            # Use fixed values for fraud transactions
            fraud_type = fraud_types[i % len(fraud_types)]
            transactions.append(
                generate_fraud_transaction(
                    f"fraud_{i}",
                    fraud_type,
                    amount=1000,
                    timestamp_offset=720,
                    currency="USD",
                    merchant_category="electronics"
                )
            )
        else:
            # Use fixed values for legitimate transactions
            transactions.append(
                generate_legitimate_transaction(
                    f"legit_{i}",
                    amount=100,
                    timestamp_offset=720,
                    currency="USD",
                    merchant_category="groceries",
                    card_present=True
                )
            )
    return transactions
