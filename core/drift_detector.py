"""
Model Drift Detection System

This module implements mechanisms to detect and handle model drift in AI models.
"""

import numpy as np
from scipy.stats import ks_2samp
import logging
from typing import Dict, Any, List
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class DriftDetector:
    def __init__(self, drift_threshold: float = 0.05):
        self.drift_threshold = drift_threshold
        self.reference_data: Dict[str, List[Any]] = {}
        self.current_data: Dict[str, List[Any]] = {}
        self.drift_status: Dict[str, bool] = {}
        self.drift_metrics: Dict[str, float] = {}
        
    def add_reference_data(self, feature_name: str, data: List[Any]) -> None:
        """Add reference data for drift detection"""
        self.reference_data[feature_name] = data
        logger.info(f"Added reference data for feature: {feature_name}")
    
    def add_current_data(self, feature_name: str, data: List[Any]) -> None:
        """Add current data for drift comparison"""
        self.current_data[feature_name] = data
        logger.info(f"Added current data for feature: {feature_name}")
    
    def detect_drift(self) -> Dict[str, bool]:
        """Detect drift for all features"""
        results = {}
        
        for feature in self.reference_data.keys():
            if feature not in self.current_data:
                logger.warning(f"No current data for feature: {feature}")
                continue
                
            ref_data = np.array(self.reference_data[feature])
            cur_data = np.array(self.current_data[feature])
            
            # Perform Kolmogorov-Smirnov test
            stat, p_value = ks_2samp(ref_data, cur_data)
            
            # Store metrics
            self.drift_metrics[feature] = p_value
            
            # Determine drift status
            drift_detected = p_value < self.drift_threshold
            self.drift_status[feature] = drift_detected
            results[feature] = drift_detected
            
            logger.info(f"Drift detection for {feature}: {drift_detected} (p-value: {p_value:.4f})")
        
        return results
    
    def get_drift_metrics(self) -> Dict[str, float]:
        """Get drift metrics for all features"""
        return self.drift_metrics
    
    def save_drift_report(self, filepath: str) -> None:
        """Save drift detection report to file"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "drift_threshold": self.drift_threshold,
            "drift_status": self.drift_status,
            "drift_metrics": self.drift_metrics,
            "reference_data_stats": {
                k: {
                    "mean": np.mean(v),
                    "std": np.std(v),
                    "count": len(v)
                } for k, v in self.reference_data.items()
            },
            "current_data_stats": {
                k: {
                    "mean": np.mean(v),
                    "std": np.std(v),
                    "count": len(v)
                } for k, v in self.current_data.items()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Saved drift detection report to {filepath}")

class ModelDriftMonitor:
    def __init__(self, drift_detector: DriftDetector, 
                 monitoring_interval: int = 60,
                 alert_threshold: int = 3):
        self.drift_detector = drift_detector
        self.monitoring_interval = monitoring_interval
        self.alert_threshold = alert_threshold
        self.consecutive_drifts: Dict[str, int] = {}
        
    def process_batch(self, batch_data: Dict[str, List[Any]]) -> None:
        """Process a batch of data and check for drift"""
        for feature, data in batch_data.items():
            self.drift_detector.add_current_data(feature, data)
        
        drift_results = self.drift_detector.detect_drift()
        
        # Update consecutive drift counts
        for feature, drift in drift_results.items():
            if drift:
                self.consecutive_drifts[feature] = self.consecutive_drifts.get(feature, 0) + 1
                if self.consecutive_drifts[feature] >= self.alert_threshold:
                    logger.warning(f"ALERT: Feature {feature} has drifted for {self.alert_threshold} consecutive checks")
            else:
                self.consecutive_drifts[feature] = 0
    
    def save_drift_report(self, filepath: str) -> None:
        """Save comprehensive drift monitoring report"""
        self.drift_detector.save_drift_report(filepath)
        
        # Add monitoring-specific information
        with open(filepath, 'r') as f:
            report = json.load(f)
        
        report["monitoring_info"] = {
            "interval_seconds": self.monitoring_interval,
            "alert_threshold": self.alert_threshold,
            "consecutive_drifts": self.consecutive_drifts
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
