# Financial Transaction Data Generation

This module provides tools for generating synthetic financial transaction data with realistic patterns for fraud detection model training and testing. It supports both fully synthetic data generation and integration with public datasets.

## Features

- **Synthetic Data Generation**: Create realistic financial transactions with configurable fraud rates
- **Public Dataset Integration**: Seamlessly work with popular financial fraud datasets
- **Data Augmentation**: Apply various augmentation techniques to increase dataset diversity
- **Balanced Datasets**: Option to balance fraud/non-fraud samples
- **Customizable**: Control over transaction characteristics, customer profiles, and fraud patterns

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. For public dataset integration, set up Kaggle API:
   - Create a Kaggle account at https://www.kaggle.com/
   - Go to Account -> Create New API Token (downloads kaggle.json)
   - Place kaggle.json in ~/.kaggle/ directory
   - Set permissions: `chmod 600 ~/.kaggle/kaggle.json`

## Usage

### Basic Usage

```python
from app.data_generator import generate_dataset

# Generate synthetic data
df = generate_dataset(
    n_transactions=10000,
    fraud_rate=0.01,
    output_file="data/transactions.csv"
)
```

### Using Public Datasets

```python
# Download and use a public dataset
df = generate_dataset(
    n_transactions=5000,
    fraud_rate=0.01,
    use_public_data=True,
    public_dataset='mlg-ulb/creditcardfraud',
    balance_data=True,
    output_file="data/creditcard_transactions.csv"
)
```

### Data Augmentation

```python
from app.data_generator import TransactionGenerator

# Create a generator with custom augmentation
generator = TransactionGenerator(
    n_customers=1000,
    augment_data=True,
    jitter_scale=0.15  # More aggressive augmentation
)

transactions = generator.generate_transactions(n_transactions=1000, fraud_rate=0.02)
```

## Available Public Datasets

1. **Kaggle Credit Card Fraud Detection**
   - Name: `mlg-ulb/creditcardfraud`
   - Description: Contains transactions made by credit cards in September 2013 by European cardholders
   - Features: V1-V28 (anonymized), Time, Amount, Class (fraud/not fraud)

2. **IEEE-CIS Fraud Detection**
   - Name: `c/ieee-fraud-detection`
   - Description: Contains transactions from e-commerce and online retail
   - Features: TransactionDT, TransactionAmt, ProductCD, card1-card6, addr1, addr2, etc.

## Data Schema

Each transaction includes the following fields:

| Field | Type | Description |
|-------|------|-------------|
| transaction_id | str | Unique transaction identifier |
| customer_id | str | Customer identifier |
| timestamp | str | Transaction timestamp (ISO format) |
| amount | float | Transaction amount |
| currency | str | Currency code (default: USD) |
| merchant_name | str | Name of the merchant |
| merchant_category | str | Category of the merchant |
| transaction_type | str | Type of transaction (PURCHASE, WITHDRAWAL, etc.) |
| location | str | Geographic location (City, Country) |
| device_id | str | Identifier for the device used |
| ip_address | str | IP address of the device |
| is_fraud | bool | Whether the transaction is fraudulent |
| fraud_type | str | Type of fraud (if applicable) |
| transaction_confidence | float | Confidence score of the transaction |
| data_source | str | Source of the data (synthetic or public dataset) |

## Advanced Usage

### Custom Data Augmentation

```python
from app.data_augmentation import DataAugmentor

# Create a custom augmentor
augmentor = DataAugmentor(
    jitter_scale=0.2,  # More aggressive jitter
    max_shift_hours=48,  # Allow larger time shifts
    swap_prob=0.15  # Higher probability of category swapping
)

# Apply augmentation to existing data
augmented_data = [augmentor.augment(transaction) for transaction in transactions]
```

### Dataset Balancing

```python
from app.data_augmentation import balance_dataset
import pandas as pd

# Load your dataset
df = pd.read_csv("transactions.csv")

# Balance the dataset (oversample minority class)
balanced_df = balance_dataset(df, 'is_fraud', method='oversample')

# Or undersample majority class
balanced_df = balance_dataset(df, 'is_fraud', method='undersample')
```

## Best Practices

1. **Start with a small dataset** to test your pipeline before generating large datasets
2. **Monitor the fraud rate** to ensure it matches your target
3. **Use data augmentation** to create more diverse training examples
4. **Balance your dataset** if you have a severe class imbalance
5. **Validate** your synthetic data to ensure it has the expected statistical properties

## Troubleshooting

- **Kaggle API errors**: Ensure your Kaggle API credentials are properly set up
- **Memory issues**: For large datasets, process data in batches
- **Unbalanced data**: Use the `balance_data=True` parameter or manually balance the dataset

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
