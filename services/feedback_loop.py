"""
Real-time Feedback Loop System

This module implements the feedback loop for model performance evaluation.
"""

import logging
from typing import Dict, Any, List
import time
from datetime import datetime

class FeedbackError(Exception):
    """Raised when feedback processing fails"""
    pass

class FeedbackLoop:
    def __init__(self, config: Dict[str, Any]):
        """Initialize feedback loop system"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.window_size = config.get("window_size", 100)
        self.check_interval = config.get("check_interval", 3600)  # 1 hour
        self.last_check = time.time()
        self.metrics = {
            "accuracy": [],
            "latency": [],
            "errors": [],
            "bias_scores": [],
            "drift_scores": []
        }
        
    def add_metric(self, metric_type: str, value: float) -> None:
        """Add metric value to the current window"""
        if metric_type not in self.metrics:
            raise FeedbackError(f"Unknown metric type: {metric_type}")
            
        self.metrics[metric_type].append(value)
        
        # Keep only the last window_size values
        if len(self.metrics[metric_type]) > self.window_size:
            self.metrics[metric_type] = self.metrics[metric_type][-self.window_size:]
    
    def calculate_metrics(self) -> Dict[str, float]:
        """Calculate aggregated metrics for current window"""
        results = {}
        
        for metric_type, values in self.metrics.items():
            if values:
                results[metric_type] = {
                    "mean": sum(values) / len(values),
                    "std": (sum((x - sum(values)/len(values))**2 for x in values) / len(values)) ** 0.5,
                    "count": len(values)
                }
        
        return results
    
    def check_performance(self) -> Dict[str, bool]:
        """Check if performance metrics meet thresholds"""
        results = self.calculate_metrics()
        thresholds = self.config.get("thresholds", {})
        alerts = {}
        
        for metric_type, stats in results.items():
            threshold = thresholds.get(metric_type, {}).get("mean", None)
            if threshold is not None and stats["mean"] > threshold:
                alerts[metric_type] = True
                self.logger.warning(
                    f"Performance alert: {metric_type} mean={stats['mean']:.2f} > threshold={threshold:.2f}"
                )
        
        return alerts
    
    def check_bias(self) -> Dict[str, float]:
        """Check for bias in predictions"""
        if not self.metrics["bias_scores"]:
            return {}
            
        mean_bias = sum(self.metrics["bias_scores"]) / len(self.metrics["bias_scores"])
        threshold = self.config.get("bias_threshold", 0.1)
        
        if mean_bias > threshold:
            self.logger.warning(
                f"Bias alert: mean bias={mean_bias:.2f} > threshold={threshold:.2f}"
            )
            return {"bias": mean_bias}
        
        return {}
    
    def check_drift(self) -> Dict[str, float]:
        """Check for model drift"""
        if not self.metrics["drift_scores"]:
            return {}
            
        mean_drift = sum(self.metrics["drift_scores"]) / len(self.metrics["drift_scores"])
        threshold = self.config.get("drift_threshold", 0.05)
        
        if mean_drift > threshold:
            self.logger.warning(
                f"Drift alert: mean drift={mean_drift:.2f} > threshold={threshold:.2f}"
            )
            return {"drift": mean_drift}
        
        return {}
    
    def process_feedback(self) -> Dict[str, Any]:
        """Process all feedback metrics"""
        if time.time() - self.last_check < self.check_interval:
            return {}
            
        self.last_check = time.time()
        
        alerts = {
            "performance": self.check_performance(),
            "bias": self.check_bias(),
            "drift": self.check_drift()
        }
        
        return alerts
    
    def trigger_retraining(self, alerts: Dict[str, Any]) -> bool:
        """Trigger model retraining if necessary"""
        if any(alerts.values()):
            self.logger.info("Retraining triggered due to performance issues")
            # Add retraining logic here
            return True
        return False
