from typing import Dict, Any, List
import random
from datetime import datetime, timedelta

class DataGenerator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def generate_transaction(self) -> Dict[str, Any]:
        """Generate a synthetic transaction."""
        amount = round(random.uniform(10, 10000), 2)
        return {
            'transaction_id': f'TXN_{random.randint(10000, 99999)}',
            'amount': amount,
            'currency': 'USD',
            'timestamp': datetime.now().isoformat(),
            'merchant': f'MERCHANT_{random.randint(100, 999)}',
            'location': {
                'lat': random.uniform(-90, 90),
                'lon': random.uniform(-180, 180)
            }
        }

    def generate_customer_data(self) -> Dict[str, Any]:
        """Generate synthetic customer data."""
        return {
            'customer_id': f'CUST_{random.randint(10000, 99999)}',
            'name': f'Customer {random.randint(1, 1000)}',
            'email': f'customer{random.randint(1, 1000)}@example.com',
            'registration_date': (
                datetime.now() - timedelta(days=random.randint(1, 365))
            ).isoformat()
        }

    def generate_batch(self, count: int) -> List[Dict[str, Any]]:
        """Generate a batch of synthetic data."""
        return [self.generate_transaction() for _ in range(count)]
