"""
Model Validation System

This module implements validation for AI models to ensure they meet performance and bias requirements.
"""

import numpy as np
from typing import Dict, Any, List, Tuple
import logging
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

class ModelValidator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = {
            "accuracy": config.get("accuracy", 0.95),
            "precision": config.get("precision", 0.90),
            "recall": config.get("recall", 0.90),
            "f1_score": config.get("f1_score", 0.92)
        }
    
    def _calculate_metrics(self, y_true: List[int], y_pred: List[int]) -> Dict[str, float]:
        """Calculate performance metrics"""
        return {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred),
            "recall": recall_score(y_true, y_pred),
            "f1_score": f1_score(y_true, y_pred)
        }
    
    def validate_performance(self, y_true: List[int], y_pred: List[int]) -> Dict[str, bool]:
        """Validate model performance against thresholds"""
        metrics = self._calculate_metrics(y_true, y_pred)
        validation = {}
        
        for metric, value in metrics.items():
            threshold = self.metrics.get(metric, 0.0)
            validation[metric] = value >= threshold
            
            if not validation[metric]:
                self.logger.warning(
                    f"Performance validation failed: {metric}={value:.2f} < {threshold:.2f}"
                )
        
        return validation
    
    def _calculate_bias_score(self, predictions: List[float], demographic: List[str]) -> Dict[str, float]:
        """Calculate bias scores for demographic groups"""
        bias_scores = {}
        
        # Group predictions by demographic
        groups = {}
        for pred, demo in zip(predictions, demographic):
            if demo not in groups:
                groups[demo] = []
            groups[demo].append(pred)
        
        # Calculate mean difference from overall mean
        overall_mean = np.mean(predictions)
        
        for group, values in groups.items():
            group_mean = np.mean(values)
            bias_score = abs(group_mean - overall_mean) / np.std(predictions)
            bias_scores[group] = min(bias_score, 1.0)
        
        return bias_scores
    
    def validate_bias(self, predictions: List[float], demographic: List[str]) -> bool:
        """Validate model predictions for bias"""
        bias_scores = self._calculate_bias_score(predictions, demographic)
        
        for group, score in bias_scores.items():
            if score > self.config.get("bias_threshold", 0.1):
                self.logger.warning(
                    f"Bias detected in group {group}: Score={score:.2f}"
                )
                return False
        
        return True
    
    def validate_drift(self, current_metrics: Dict[str, float], reference_metrics: Dict[str, float]) -> bool:
        """Validate model for concept drift"""
        drift_threshold = self.config.get("drift_threshold", 0.05)
        
        for metric in current_metrics:
            if metric in reference_metrics:
                diff = abs(current_metrics[metric] - reference_metrics[metric])
                if diff > drift_threshold:
                    self.logger.warning(
                        f"Model drift detected: {metric} changed by {diff:.2f}"
                    )
                    return False
        
        return True
