"""
Monitoring Dashboard Configuration

This module defines the configuration for the monitoring dashboard.
"""

import logging
from typing import Dict, Any, List

class DashboardConfig:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = {
            "performance": [
                {"name": "model_accuracy", "unit": "%", "threshold": 95},
                {"name": "model_latency", "unit": "ms", "threshold": 500},
                {"name": "error_rate", "unit": "%", "threshold": 1}
            ],
            "compliance": [
                {"name": "gdpr_violations", "unit": "count", "threshold": 0},
                {"name": "dpdp_violations", "unit": "count", "threshold": 0},
                {"name": "encryption_failures", "unit": "count", "threshold": 0}
            ],
            "bias": [
                {"name": "demographic_bias", "unit": "score", "threshold": 0.1},
                {"name": "prediction_variance", "unit": "score", "threshold": 0.1}
            ],
            "system": [
                {"name": "cpu_usage", "unit": "%", "threshold": 80},
                {"name": "memory_usage", "unit": "%", "threshold": 80},
                {"name": "disk_usage", "unit": "%", "threshold": 80}
            ]
        }
    
    def get_metrics(self, category: str) -> List[Dict[str, Any]]:
        """Get metrics for a specific category"""
        return self.metrics.get(category, [])
    
    def get_threshold(self, metric_name: str) -> float:
        """Get threshold for a specific metric"""
        for category, metrics in self.metrics.items():
            for metric in metrics:
                if metric["name"] == metric_name:
                    return metric["threshold"]
        return 0.0
    
    def validate_metrics(self, metrics: Dict[str, float]) -> Dict[str, bool]:
        """Validate metrics against thresholds"""
        alerts = {}
        for metric_name, value in metrics.items():
            threshold = self.get_threshold(metric_name)
            if value > threshold:
                alerts[metric_name] = True
                self.logger.warning(
                    f"Metric {metric_name} exceeded threshold: {value} > {threshold}"
                )
        return alerts
