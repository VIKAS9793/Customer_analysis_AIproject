"""
Data augmentation and public dataset integration for financial transactions.
"""

import os
import random
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sklearn.utils import resample
from sklearn.preprocessing import StandardScaler
from enum import Enum

class DataAugmentor:
    """Handles data augmentation for transaction data."""
    
    def __init__(self, jitter_scale: float = 0.1):
        """Initialize the data augmentor.
        
        Args:
            jitter_scale: Controls the amount of jitter to add (0-1)
        """
        self.jitter_scale = jitter_scale
        self.scaler = StandardScaler()
    
    def add_jitter(self, amount: float, scale: Optional[float] = None) -> float:
        """Add random jitter to a numerical value."""
        if scale is None:
            scale = self.jitter_scale
        jitter = 1 + random.uniform(-scale, scale)
        return max(0.01, amount * jitter)  # Ensure positive amount
    
    def augment_timestamps(self, timestamps: List[datetime], max_shift_hours: int = 24) -> List[datetime]:
        """Randomly shift timestamps within a time window."""
        return [
            ts + timedelta(hours=random.uniform(-max_shift_hours, max_shift_hours))
            for ts in timestamps
        ]
    
    def augment_categorical(self, values: List[Any], swap_prob: float = 0.1) -> List[Any]:
        """Randomly swap categorical values with a small probability."""
        unique_values = list(set(values))
        if len(unique_values) < 2:
            return values
            
        return [
            random.choice([v for v in unique_values if v != val]) 
            if random.random() < swap_prob else val 
            for val in values
        ]
    
    def augment_numerical(self, values: List[float], scale: float = 0.1) -> List[float]:
        """Add scaled random noise to numerical values."""
        if not values:
            return values
            
        values_array = np.array(values).reshape(-1, 1)
        if len(set(values_array.flatten())) > 1:  # Only fit if not all values are the same
            self.scaler.fit(values_array)
            scaled = self.scaler.transform(values_array)
            # Add noise and inverse transform
            noise = np.random.normal(0, scale, size=scaled.shape)
            augmented = self.scaler.inverse_transform(scaled + noise)
            return [max(0, x[0]) for x in augmented]  # Ensure non-negative values
        return values


class PublicDatasetLoader:
    """Handles loading and preprocessing of public financial datasets."""
    
    @staticmethod
    def load_kaggle_creditcard(filepath: str, sample_size: Optional[int] = None) -> pd.DataFrame:
        """Load and preprocess the Kaggle Credit Card Fraud Detection dataset."""
        try:
            df = pd.read_csv(filepath)
            if sample_size and len(df) > sample_size:
                df = df.sample(n=sample_size, random_state=42)
                
            # Add metadata to match our schema
            df['transaction_type'] = 'PURCHASE'
            df['merchant_category'] = 'RETAIL'
            df['is_fraud'] = df['Class']
            df['amount'] = df['Amount']
            return df
            
        except Exception as e:
            print(f"Error loading Kaggle Credit Card dataset: {e}")
            return pd.DataFrame()
    
    @classmethod
    def load_public_dataset(cls, dataset_name: str, filepath: str, **kwargs) -> pd.DataFrame:
        """Load a public dataset by name."""
        if dataset_name == 'kaggle_creditcard':
            return cls.load_kaggle_creditcard(filepath, **kwargs)
        else:
            raise ValueError(f"Unsupported dataset: {dataset_name}")


def download_kaggle_dataset(dataset_name: str, output_dir: str = 'data') -> str:
    """Download a dataset from Kaggle.
    
    Args:
        dataset_name: Name of the dataset in format 'username/dataset-name'
        output_dir: Directory to save the downloaded dataset
        
    Returns:
        Path to the downloaded dataset directory
    """
    try:
        import opendatasets as od
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Download the dataset
        dataset_path = os.path.join(output_dir, dataset_name.split('/')[-1])
        if not os.path.exists(dataset_path):
            od.download(f"https://www.kaggle.com/datasets/{dataset_name}", 
                       data_dir=output_dir)
            
        return dataset_path
        
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        return ""

def balance_dataset(df: pd.DataFrame, target_column: str, method: str = 'undersample', 
                   random_state: int = 42) -> pd.DataFrame:
    """Balance a dataset by undersampling or oversampling.
    
    Args:
        df: Input DataFrame
        target_column: Name of the target column
        method: 'undersample' or 'oversample'
        random_state: Random seed for reproducibility
        
    Returns:
        Balanced DataFrame
    """
    if target_column not in df.columns:
        return df
        
    # Separate majority and minority classes
    df_majority = df[df[target_column] == 0]
    df_minority = df[df[target_column] == 1]
    
    if method == 'undersample':
        # Undersample majority class
        df_majority = resample(df_majority,
                             replace=False,
                             n_samples=len(df_minority),
                             random_state=random_state)
        
        # Combine minority class with undersampled majority class
        return pd.concat([df_majority, df_minority])
        
    elif method == 'oversample':
        # Oversample minority class
        df_minority_oversampled = resample(df_minority,
                                         replace=True,
                                         n_samples=len(df_majority),
                                         random_state=random_state)
        
        # Combine majority class with oversampled minority class
        return pd.concat([df_majority, df_minority_oversampled])
    
    return df
