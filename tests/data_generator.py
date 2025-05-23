import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
from pathlib import Path

class TestDataGenerator:
    """Generator for synthetic test data for fraud detection."""
    
    def __init__(self, seed: int = None):
        """Initialize the data generator.
        
        Args:
            seed: Optional seed for random number generation
        """
        if seed is not None:
            random.seed(seed)
        
    def generate_test_data(
        self,
        num_transactions: int = 1000,
        fraud_rate: float = 0.05,
        output_file: str = "test_data.json"
    ) -> List[Dict[str, Any]]:
        """Generate synthetic test data for fraud detection.

        Args:
            num_transactions: Number of transactions to generate
            fraud_rate: Percentage of transactions that are fraudulent
            output_file: Path to save the generated data

        Returns:
            List of transaction dictionaries
        """
        transactions = []
        fraud_count = int(num_transactions * fraud_rate)
        
        # Generate fraud patterns
        fraud_patterns = [
            # High-risk country transactions
            {"country": "Nigeria", "amount_range": (1000, 5000), "category": "electronics"},
            # Card-not-present fraud
            {"card_present": False, "amount_range": (500, 2000), "category": "travel"},
            # Account takeover
            {"new_account": True, "unusual_pattern": True, "amount_range": (200, 1000)},
            # Identity theft
            {"multiple_locations": True, "unusual_device": True, "amount_range": (300, 1500)}
        ]
        
        # Generate legitimate patterns
        legitimate_patterns = [
            {"country": "US", "amount_range": (10, 200), "category": "groceries"},
            {"country": "UK", "amount_range": (20, 100), "category": "dining"},
            {"country": "Germany", "amount_range": (50, 300), "category": "transport"}
        ]
        
        # Generate fraudulent transactions
        for i in range(fraud_count):
            pattern = random.choice(fraud_patterns)
            transaction = {
                "transaction_id": f"fraud_{i}",
                "timestamp": datetime.now().isoformat(),
                "amount": random.uniform(*pattern["amount_range"]),
                "country": pattern.get("country", "Unknown"),
                "category": pattern.get("category", "unknown"),
                "card_present": pattern.get("card_present", True),
                "is_fraud": True,
                "merchant_category": pattern.get("category", "unknown"),
                "ip_country_match": False,
                "device_id_consistent": False
            }
            transactions.append(transaction)
        
        # Generate legitimate transactions
        for i in range(num_transactions - fraud_count):
            pattern = random.choice(legitimate_patterns)
            transaction = {
                "transaction_id": f"legit_{i}",
                "timestamp": datetime.now().isoformat(),
                "amount": random.uniform(*pattern["amount_range"]),
                "country": pattern["country"],
                "category": pattern["category"],
                "card_present": True,
                "is_fraud": False,
                "merchant_category": pattern["category"],
                "ip_country_match": True,
                "device_id_consistent": True
            }
            transactions.append(transaction)
        
        # Shuffle the transactions
        random.shuffle(transactions)
        
        # Save to file
        with open(output_file, "w") as f:
            json.dump(transactions, f, indent=2)
        
        return transactions
    
    def generate_edge_cases(self) -> List[Dict[str, Any]]:
        """Generate edge case scenarios for testing."""
        edge_cases = [
            # High-value legitimate transaction
            {
                "transaction_id": "high_value_legit",
                "amount": 5000,
                "category": "travel",
                "country": "US",
                "is_fraud": False,
                "merchant_category": "travel",
                "ip_country_match": True,
                "device_id_consistent": True
            },
            # Multiple rapid transactions
            {
                "transaction_id": "rapid_1",
                "amount": 1000,
                "category": "electronics",
                "country": "US",
                "is_fraud": True,
                "merchant_category": "electronics",
                "ip_country_match": False,
                "device_id_consistent": False
            },
            # Identity theft pattern
            {
                "transaction_id": "identity_theft",
                "amount": 800,
                "category": "retail",
                "country": "US",
                "is_fraud": True,
                "merchant_category": "retail",
                "ip_country_match": False,
                "device_id_consistent": False,
                "multiple_locations": True,
                "new_account": True
            }
        ]
        return edge_cases
    
    def generate_model_comparison_data(
        self,
        num_transactions: int = 1000,
        fraud_rate: float = 0.05
    ) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Generate data for model comparison.
        
        Returns:
            Tuple of (ground_truth_data, model_predictions)
        """
        # Generate ground truth data
        ground_truth = self.generate_test_data(num_transactions, fraud_rate)
        
        # Generate model predictions (simulating two different models)
        model1_predictions = []
        model2_predictions = []
        
        for tx in ground_truth:
            # Model 1: More conservative
            confidence = 0.9 if tx["is_fraud"] else 0.1
            model1_predictions.append({
                "transaction_id": tx["transaction_id"],
                "decision": "fraud" if tx["is_fraud"] else "legitimate",
                "confidence": confidence
            })
            
            # Model 2: More aggressive
            confidence = 0.95 if tx["is_fraud"] else 0.05
            model2_predictions.append({
                "transaction_id": tx["transaction_id"],
                "decision": "fraud" if tx["is_fraud"] else "legitimate",
                "confidence": confidence
            })
        
        return ground_truth, (model1_predictions, model2_predictions)
