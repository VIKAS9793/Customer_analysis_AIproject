"""
Synthetic Financial Transaction Data Generator

This module generates realistic financial transaction data for fraud detection model training and testing.
Supports both synthetic data generation and integration with public datasets.
"""

import os
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import numpy as np
import pandas as pd
from faker import Faker

from .data_augmentation import DataAugmentor, PublicDatasetLoader, download_kaggle_dataset, balance_dataset

class TransactionType(Enum):
    """Types of financial transactions."""
    PURCHASE = "PURCHASE"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER = "TRANSFER"
    PAYMENT = "PAYMENT"
    DEPOSIT = "DEPOSIT"

class MerchantCategory(Enum):
    """Common merchant categories for transactions."""
    GROCERY = "GROCERY"
    RETAIL = "RETAIL"
    TRAVEL = "TRAVEL"
    ENTERTAINMENT = "ENTERTAINMENT"
    UTILITIES = "UTILITIES"
    ONLINE_SERVICES = "ONLINE_SERVICES"
    GAMBLING = "GAMBLING"
    OTHER = "OTHER"

class TransactionGenerator:
    """Generates synthetic financial transaction data with support for public datasets."""

    def __init__(self, n_customers: int = 1000, seed: Optional[int] = None, 
                 augment_data: bool = True, jitter_scale: float = 0.1):
        """Initialize the transaction generator.
        
        Args:
            n_customers: Number of unique customers to generate
            seed: Random seed for reproducibility
            augment_data: Whether to apply data augmentation
            jitter_scale: Scale of jitter to apply during augmentation (0-1)
        """
        self.fake = Faker()
        self.n_customers = n_customers
        self.customer_profiles = []
        self.augmentor = DataAugmentor(jitter_scale=jitter_scale) if augment_data else None
        self.dataset_loader = PublicDatasetLoader()
        
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            self.fake.seed(seed)
        
        self._generate_customer_profiles()
    
    def _generate_customer_profiles(self):
        """Generate customer profiles with realistic attributes."""
        for _ in range(self.n_customers):
            profile = {
                'customer_id': str(uuid.uuid4()),
                'name': self.fake.name(),
                'email': self.fake.email(),
                'address': self.fake.address().replace('\n', ', '),
                'phone': self.fake.phone_number(),
                'account_balance': max(1000, np.random.lognormal(7, 0.5)),
                'account_age_days': random.randint(30, 3650),  # 1 month to 10 years
                'avg_transaction_amount': max(10, np.random.lognormal(4, 0.8)),
                'transaction_frequency': random.choice(['low', 'medium', 'high']),
                'preferred_categories': random.sample(
                    [cat.value for cat in MerchantCategory], 
                    k=random.randint(2, 4)
                )
            }
            self.customer_profiles.append(profile)
    
    def _generate_transaction_amount(self, customer: Dict[str, Any]) -> float:
        """Generate a transaction amount based on customer profile."""
        base_amount = customer['avg_transaction_amount']
        # Add some randomness to the amount
        amount = np.random.lognormal(np.log(base_amount), 0.5)
        return round(amount, 2)
    
    def _generate_timestamp(self, days_back: int = 30) -> str:
        """Generate a random timestamp within the last N days."""
        random_days = random.uniform(0, days_back)
        random_seconds = random.uniform(0, 60 * 60 * 24)  # Random seconds in a day
        timestamp = datetime.now() - timedelta(days=random_days, seconds=random_seconds)
        return timestamp.isoformat()
    
    def _apply_augmentation(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Apply data augmentation to a transaction if enabled."""
        if not self.augmentor:
            return transaction
            
        augmented = transaction.copy()
        
        # Add jitter to amount
        augmented['amount'] = round(self.augmentor.add_jitter(augmented['amount']), 2)
        
        # Add jitter to timestamp if it's a string
        if isinstance(augmented['timestamp'], str):
            try:
                timestamp = datetime.fromisoformat(augmented['timestamp'])
                augmented['timestamp'] = self.augmentor.augment_timestamps([timestamp])[0].isoformat()
            except (ValueError, TypeError):
                pass
        
        # Possibly swap merchant category
        if random.random() < 0.05:  # 5% chance to change category
            augmented['merchant_category'] = random.choice(
                [cat for cat in MerchantCategory if cat.value != augmented.get('merchant_category', '')]
            ).value
            
        return augmented
    
    def generate_transactions(self, n_transactions: int = 1000, fraud_rate: float = 0.01,
                            use_public_data: bool = False, public_dataset: Optional[str] = None,
                            public_data_path: Optional[str] = None, balance_data: bool = False) -> List[Dict[str, Any]]:
        """Generate transaction data with optional public dataset integration.
        
        Args:
            n_transactions: Number of transactions to generate
            fraud_rate: Target fraud rate (approximate)
            use_public_data: Whether to use public dataset as base
            public_dataset: Name of public dataset to use (if use_public_data is True)
            public_data_path: Path to the downloaded public dataset file
            balance_data: Whether to balance the dataset (only applies to public data)
            
        Returns:
            List of transaction dictionaries
        """
        if use_public_data and public_dataset and public_data_path:
            return self._generate_from_public_data(public_dataset, public_data_path, n_transactions, fraud_rate, balance_data)
        else:
            return self._generate_synthetic_transactions(n_transactions, fraud_rate)
    
    def _generate_synthetic_transactions(self, n_transactions: int, fraud_rate: float) -> List[Dict[str, Any]]:
        """Generate purely synthetic transaction data."""
        transactions = []
        n_fraud = int(n_transactions * fraud_rate)
        
        for i in range(n_transactions):
            customer = random.choice(self.customer_profiles)
            is_fraud = i < n_fraud
            
            # For fraudulent transactions, sometimes use a different customer's profile
            if is_fraud and random.random() < 0.3:  # 30% of fraud uses a different customer profile
                other_customers = [c for c in self.customer_profiles if c['customer_id'] != customer['customer_id']]
                if other_customers:
                    customer = random.choice(other_customers)
            
            transaction_type = random.choice(list(TransactionType)).value
            merchant_category = random.choice(customer['preferred_categories'])
            
            # Generate amount based on transaction type and customer profile
            if transaction_type == TransactionType.PURCHASE.value:
                amount = self._generate_transaction_amount(customer)
            elif transaction_type == TransactionType.WITHDRAWAL.value:
                amount = self._generate_transaction_amount(customer) * 2  # Withdrawals tend to be larger
            else:
                amount = self._generate_transaction_amount(customer) * random.uniform(0.5, 1.5)
            
            # Adjust amount for fraudulent transactions
            if is_fraud:
                amount *= random.uniform(3, 10)  # Fraudulent transactions are typically larger
                if random.random() < 0.1:  # 10% of fraud is very small amounts
                    amount = random.uniform(0.01, 1.00)
            
            transaction = {
                'transaction_id': str(uuid.uuid4()),
                'customer_id': customer['customer_id'],
                'timestamp': self._generate_timestamp(),
                'amount': round(amount, 2),
                'currency': 'USD',
                'merchant_name': self.fake.company(),
                'merchant_category': merchant_category,
                'transaction_type': transaction_type,
                'location': f"{self.fake.city()}, {self.fake.country_code()}",
                'device_id': f"{random.choice(['MOB', 'WEB', 'POS'])}-{self.fake.md5()[:8]}",
                'ip_address': self.fake.ipv4(),
                'is_fraud': is_fraud,
                'fraud_type': random.choice(['card_not_present', 'card_present', 'identity_theft', 'account_takeover']) if is_fraud else None,
                'transaction_confidence': random.uniform(0.7, 0.99) if not is_fraud else random.uniform(0.01, 0.8),
                'data_source': 'synthetic'
            }
            
            # Apply augmentation if enabled
            if self.augmentor:
                transaction = self._apply_augmentation(transaction)
            
            transactions.append(transaction)
        
        return transactions
    
    def _generate_from_public_data(self, dataset_name: str, filepath: str, 
                                 n_samples: int, target_fraud_rate: float,
                                 balance_data: bool = False) -> List[Dict[str, Any]]:
        """Generate transactions based on a public dataset with augmentation."""
        try:
            # Load the public dataset
            df = self.dataset_loader.load_public_dataset(dataset_name, filepath, sample_size=n_samples)
            
            if df.empty:
                print("Failed to load public dataset. Falling back to synthetic data generation.")
                return self._generate_synthetic_transactions(n_samples, target_fraud_rate)
            
            # Balance the dataset if requested
            if balance_data and 'is_fraud' in df.columns:
                df = balance_dataset(df, 'is_fraud')
            
            # Sample the requested number of transactions if needed
            if len(df) > n_samples:
                df = df.sample(n=n_samples, random_state=42)
            
            # Convert to our transaction format
            transactions = []
            for _, row in df.iterrows():
                is_fraud = bool(row.get('is_fraud', row.get('Class', 0)))
                
                transaction = {
                    'transaction_id': str(uuid.uuid4()),
                    'customer_id': f"PUBLIC_{row.get('customer_id', str(uuid.uuid4())[:8])}",
                    'timestamp': self._generate_timestamp(),
                    'amount': float(row.get('amount', row.get('TransactionAmt', random.uniform(1, 1000)))),
                    'currency': 'USD',
                    'merchant_name': self.fake.company(),
                    'merchant_category': random.choice(list(MerchantCategory)).value,
                    'transaction_type': row.get('transaction_type', random.choice(list(TransactionType)).value),
                    'location': f"{self.fake.city()}, {self.fake.country_code()}",
                    'device_id': f"{random.choice(['MOB', 'WEB', 'POS'])}-{self.fake.md5()[:8]}",
                    'ip_address': self.fake.ipv4(),
                    'is_fraud': is_fraud,
                    'fraud_type': random.choice(['card_not_present', 'card_present', 'identity_theft', 'account_takeover']) if is_fraud else None,
                    'transaction_confidence': random.uniform(0.7, 0.99) if not is_fraud else random.uniform(0.01, 0.8),
                    'data_source': f'public_{dataset_name}'
                }
                
                # Apply augmentation if enabled
                if self.augmentor:
                    transaction = self._apply_augmentation(transaction)
                
                transactions.append(transaction)
            
            return transactions
            
        except Exception as e:
            print(f"Error processing public dataset: {e}")
            print("Falling back to synthetic data generation...")
            return self._generate_synthetic_transactions(n_samples, target_fraud_rate)

def generate_dataset(n_transactions: int = 10000, fraud_rate: float = 0.01,
                    use_public_data: bool = False, public_dataset: Optional[str] = None,
                    public_data_path: Optional[str] = None, balance_data: bool = False,
                    output_file: Optional[str] = None, seed: Optional[int] = 42) -> pd.DataFrame:
    """Generate a transaction dataset with optional public dataset integration.
    
    Args:
        n_transactions: Total number of transactions to generate
        fraud_rate: Target fraud rate (approximate)
        use_public_data: Whether to use public dataset as base
        public_dataset: Name of public dataset to use (if use_public_data is True)
        public_data_path: Path to the downloaded public dataset file
        balance_data: Whether to balance the dataset (only applies to public data)
        output_file: Optional path to save the dataset as CSV
        seed: Random seed for reproducibility
        
    Returns:
        DataFrame containing the generated transactions
    """
    generator = TransactionGenerator(n_customers=1000, seed=seed, augment_data=True)
    
    # Download dataset if needed
    if use_public_data and public_dataset and not public_data_path:
        print(f"Downloading {public_dataset} dataset...")
        public_data_path = download_kaggle_dataset(public_dataset)
    
    # Generate transactions
    transactions = generator.generate_transactions(
        n_transactions=n_transactions,
        fraud_rate=fraud_rate,
        use_public_data=use_public_data,
        public_dataset=public_dataset,
        public_data_path=public_data_path,
        balance_data=balance_data
    )
    
    df = pd.DataFrame(transactions)
    
    # Save to file if requested
    if output_file:
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        df.to_csv(output_file, index=False)
        print(f"Generated {len(df)} transactions ({df['is_fraud'].sum()} fraudulent) saved to {output_file}")
    
    return df


def download_public_dataset(dataset_name: str, output_dir: str = 'data') -> str:
    """Download a public dataset.
    
    Args:
        dataset_name: Name of the dataset (e.g., 'kaggle/creditcardfraud')
        output_dir: Directory to save the downloaded dataset
        
    Returns:
        Path to the downloaded dataset directory
    """
    return download_kaggle_dataset(dataset_name, output_dir)


if __name__ == "__main__":
    # Example 1: Generate synthetic data
    print("Generating synthetic data...")
    df_synth = generate_dataset(
        n_transactions=5000,
        fraud_rate=0.01,
        output_file="data/synthetic_transactions.csv"
    )
    
    # Example 2: Use public dataset (requires Kaggle API setup)
    # print("\nUsing public dataset...")
    # df_public = generate_dataset(
    #     n_transactions=5000,
    #     fraud_rate=0.01,
    #     use_public_data=True,
    #     public_dataset='mlg-ulb/creditcardfraud',
    #     public_data_path='data/creditcardfraud/creditcard.csv',
    #     balance_data=True,
    #     output_file="data/public_transactions.csv"
    # )
