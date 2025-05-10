"""
Bias Detection System

This module implements bias detection and mitigation for the fraud detection system.
"""

import numpy as np
from typing import Dict, Any, List, Tuple
import logging
from collections import defaultdict
import pandas as pd
from scipy.stats import ttest_ind

class BiasError(Exception):
    """Raised when bias is detected in the system"""
    pass

class BiasDetector:
    def __init__(self, config: Dict[str, Any]):
        """Initialize bias detector with configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.demographic_categories = [
            "age_group",
            "gender",
            "location",
            "income_bracket"
        ]
        self.bias_threshold = config.get("bias_threshold", 0.1)
        self.significance_level = config.get("significance_level", 0.05)
    
    def _calculate_demographic_metrics(self, predictions: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """Calculate metrics for each demographic category"""
        metrics = defaultdict(lambda: defaultdict(list))
        
        for prediction in predictions:
            for category in self.demographic_categories:
                if category in prediction:
                    metrics[category][prediction[category]].append(prediction["score"])
        
        return metrics
    
    def _calculate_bias_score(self, group_scores: List[float], overall_scores: List[float]) -> float:
        """Calculate bias score for a demographic group using statistical methods"""
        if not group_scores or not overall_scores:
            return 0.0
            
        group_mean = np.mean(group_scores)
        overall_mean = np.mean(overall_scores)
        
        # Calculate standardized difference
        if np.std(overall_scores) == 0:
            return 0.0
            
        # Calculate statistical significance
        t_stat, p_value = ttest_ind(group_scores, overall_scores, equal_var=False)
        
        # Calculate bias score
        bias_score = abs(group_mean - overall_mean) / np.std(overall_scores)
        
        # Adjust score based on statistical significance
        if p_value > self.significance_level:
            return 0.0  # Not statistically significant
            
        return min(bias_score, 1.0)
    
    def _calculate_demographic_disparity(self, predictions: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """Calculate demographic disparity metrics"""
        metrics = self._calculate_demographic_metrics(predictions)
        overall_scores = [p["score"] for p in predictions]
        
        disparities = {}
        
        for category, groups in metrics.items():
            disparities[category] = {}
            
            # Calculate overall positive rate
            overall_positive = sum(1 for score in overall_scores if score > 0.5)
            overall_rate = overall_positive / len(overall_scores)
            
            for group, scores in groups.items():
                # Calculate group positive rate
                group_positive = sum(1 for score in scores if score > 0.5)
                group_rate = group_positive / len(scores)
                
                # Calculate disparity ratio
                disparity = group_rate / overall_rate if overall_rate > 0 else 0
                disparities[category][group] = disparity
                
                if abs(disparity - 1) > self.bias_threshold:
                    self.logger.warning(
                        f"Demographic disparity detected in {category}={group}: Ratio={disparity:.2f}"
                    )
        
        return disparities
    
    def detect_bias(self, predictions: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """Detect bias across demographic categories using multiple methods"""
        metrics = self._calculate_demographic_metrics(predictions)
        overall_scores = [p["score"] for p in predictions]
        
        bias_scores = {}
        disparities = self._calculate_demographic_disparity(predictions)
        
        for category, groups in metrics.items():
            bias_scores[category] = {}
            
            for group, scores in groups.items():
                # Calculate bias score
                bias_score = self._calculate_bias_score(scores, overall_scores)
                
                # Combine with disparity score
                disparity_score = abs(disparities[category][group] - 1)
                combined_score = (bias_score + disparity_score) / 2
                
                bias_scores[category][group] = combined_score
                
                if combined_score > self.bias_threshold:
                    self.logger.warning(
                        f"Bias detected in {category}={group}: Score={combined_score:.2f}"
                    )
        
        return bias_scores
    
    def validate_fairness(self, predictions: List[Dict[str, Any]]) -> bool:
        """Validate that predictions are fair across demographic groups"""
        bias_scores = self.detect_bias(predictions)
        
        # Check for any bias above threshold
        for category, groups in bias_scores.items():
            for group, score in groups.items():
                if score > self.bias_threshold:
                    raise BiasError(
                        f"Bias detected in {category}={group}: Score={score:.2f}"
                    )
        
        # Additional fairness checks
        self._check_demographic_coverage(predictions)
        self._check_outlier_bias(predictions)
        
        return True
    
    def _check_demographic_coverage(self, predictions: List[Dict[str, Any]]) -> None:
        """Check if all demographic groups have sufficient representation"""
        metrics = self._calculate_demographic_metrics(predictions)
        
        for category, groups in metrics.items():
            for group, scores in groups.items():
                if len(scores) < self.config.get("min_samples", 30):
                    self.logger.warning(
                        f"Insufficient samples for {category}={group}: {len(scores)} samples"
                    )
    
    def _check_outlier_bias(self, predictions: List[Dict[str, Any]]) -> None:
        """Check for outlier bias in predictions"""
        scores = [p["score"] for p in predictions]
        q1 = np.percentile(scores, 25)
        q3 = np.percentile(scores, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = [s for s in scores if s < lower_bound or s > upper_bound]
        
        if len(outliers) / len(scores) > self.config.get("outlier_threshold", 0.05):
            self.logger.warning(
                f"High outlier rate detected: {len(outliers)/len(scores)*100:.1f}%"
            )
