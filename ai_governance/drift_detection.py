"""
Drift Detection Implementation

This module implements drift detection for the FinConnectAI system.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import numpy as np
from scipy import stats
import json
from pathlib import Path

class DriftDetector:
    def __init__(self, config: Dict[str, Any]):
        """Initialize drift detector with configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Drift detection configuration
        self.detection_config = {
            "window_size": config.get("window_size", 1000),
            "threshold": config.get("drift_threshold", 0.05),
            "metrics": config.get("drift_metrics", ["accuracy", "error_rate", "latency"]),
            "statistical_test": config.get("statistical_test", "ks_test")
        }
        
        # Initialize state
        self.baseline_distribution = {}
        self.current_window = []
        self.drift_history = []
        
    def update_baseline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update baseline distribution"""
        try:
            # Calculate baseline statistics
            baseline_stats = self._calculate_statistics(data)
            
            # Store baseline
            self.baseline_distribution = {
                "stats": baseline_stats,
                "timestamp": datetime.now().isoformat(),
                "sample_size": len(data.get("samples", [])),
                "metrics": self.detection_config["metrics"]
            }
            
            return self.baseline_distribution
        except Exception as e:
            self.logger.error(f"Baseline update failed: {str(e)}")
            raise
            
    def detect_drift(self, current_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect drift in current data"""
        try:
            # Calculate current statistics
            current_stats = self._calculate_statistics(current_data)
            
            # Perform drift detection
            drift_results = self._perform_drift_detection(current_stats)
            
            # Update drift history
            self._update_drift_history(drift_results)
            
            return drift_results
        except Exception as e:
            self.logger.error(f"Drift detection failed: {str(e)}")
            raise
            
    def _calculate_statistics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate statistics for drift detection"""
        stats_result = {}
        samples = data.get("samples", [])
        
        for metric in self.detection_config["metrics"]:
            if metric in data:
                metric_values = [sample.get(metric, 0) for sample in samples]
                stats_result[metric] = {
                    "mean": np.mean(metric_values),
                    "std": np.std(metric_values),
                    "min": np.min(metric_values),
                    "max": np.max(metric_values),
                    "distribution": np.histogram(metric_values, bins=10)
                }
                
        return stats_result
        
    def _perform_drift_detection(self, current_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Perform drift detection between baseline and current data"""
        drift_detected = False
        drift_metrics = {}
        
        for metric in self.detection_config["metrics"]:
            if metric in current_stats and metric in self.baseline_distribution["stats"]:
                # Perform statistical test
                p_value = self._statistical_test(
                    self.baseline_distribution["stats"][metric],
                    current_stats[metric]
                )
                
                # Check for drift
                drift_metrics[metric] = {
                    "drift_detected": p_value < self.detection_config["threshold"],
                    "p_value": p_value,
                    "severity": self._calculate_drift_severity(p_value)
                }
                
                if drift_metrics[metric]["drift_detected"]:
                    drift_detected = True
                    
        return {
            "drift_detected": drift_detected,
            "timestamp": datetime.now().isoformat(),
            "metrics": drift_metrics,
            "threshold": self.detection_config["threshold"]
        }
        
    def _statistical_test(self, baseline_stats: Dict[str, Any], current_stats: Dict[str, Any]) -> float:
        """Perform statistical test for drift detection"""
        if self.detection_config["statistical_test"] == "ks_test":
            # Kolmogorov-Smirnov test
            _, p_value = stats.ks_2samp(
                baseline_stats["distribution"][0],
                current_stats["distribution"][0]
            )
        else:
            # Default to t-test
            _, p_value = stats.ttest_ind(
                [baseline_stats["mean"]],
                [current_stats["mean"]]
            )
            
        return p_value
        
    def _calculate_drift_severity(self, p_value: float) -> str:
        """Calculate drift severity based on p-value"""
        if p_value < 0.01:
            return "high"
        elif p_value < 0.05:
            return "medium"
        else:
            return "low"
            
    def _update_drift_history(self, drift_result: Dict[str, Any]) -> None:
        """Update drift detection history"""
        self.drift_history.append(drift_result)
        
        # Maintain history size
        max_history = self.config.get("max_history_size", 1000)
        if len(self.drift_history) > max_history:
            self.drift_history = self.drift_history[-max_history:]
            
    def get_drift_history(self) -> List[Dict[str, Any]]:
        """Get drift detection history"""
        return self.drift_history
        
    def get_drift_statistics(self) -> Dict[str, Any]:
        """Get drift detection statistics"""
        if not self.drift_history:
            return {}
            
        total_checks = len(self.drift_history)
        drift_detected = sum(1 for result in self.drift_history if result["drift_detected"])
        
        return {
            "total_checks": total_checks,
            "drift_detected_count": drift_detected,
            "drift_frequency": drift_detected / total_checks if total_checks > 0 else 0,
            "last_check": self.drift_history[-1] if self.drift_history else None,
            "metrics_summary": self._calculate_metrics_summary()
        }
        
    def _calculate_metrics_summary(self) -> Dict[str, Any]:
        """Calculate summary statistics for drift metrics"""
        summary = {}
        
        for metric in self.detection_config["metrics"]:
            metric_drifts = [
                result["metrics"][metric]["drift_detected"]
                for result in self.drift_history
                if metric in result["metrics"]
            ]
            
            if metric_drifts:
                drift_count = sum(1 for drift in metric_drifts if drift)
                summary[metric] = {
                    "drift_frequency": drift_count / len(metric_drifts),
                    "total_drifts": drift_count
                }
                
        return summary
