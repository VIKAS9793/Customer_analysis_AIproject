"""
Prometheus Metrics Exporter

This module exports metrics for monitoring and alerting.
"""

from prometheus_client import start_http_server, Gauge, Counter, Histogram
import logging
from typing import Dict, Any
import time

class MonitoringError(Exception):
    """Raised when monitoring fails"""
    pass

class PrometheusExporter:
    def __init__(self, config: Dict[str, Any]):
        """Initialize Prometheus exporter"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        # Initialize metrics based on configuration
        self.metrics = {
            # Model Performance Metrics
            "model_accuracy": Gauge(
                "model_accuracy",
                "Model accuracy percentage",
                ["model"]
            ),
            "model_latency": Histogram(
                "model_latency",
                "Model response time in milliseconds",
                ["model"],
                buckets=[.005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5, 5.0, 7.5, 10.0]
            ),
            "error_count": Counter(
                "error_count",
                "Number of errors",
                ["type"]
            ),
            "error_rate": Gauge(
                "error_rate",
                "Error rate per request",
                ["model"]
            ),
            "false_positive_rate": Gauge(
                "false_positive_rate",
                "False positive rate",
                ["model"]
            ),
            "false_negative_rate": Gauge(
                "false_negative_rate",
                "False negative rate",
                ["model"]
            ),
            
            # Transaction Metrics
            "transaction_count": Counter(
                "transaction_count",
                "Number of transactions processed",
                ["status"]
            ),
            "transaction_latency": Histogram(
                "transaction_latency",
                "Transaction processing time in seconds",
                ["type"],
                buckets=[.1, .25, .5, .75, 1.0, 2.5, 5.0, 7.5, 10.0]
            ),
            
            # AI Governance Metrics
            "bias_score": Gauge(
                "bias_score",
                "Bias score for demographic groups",
                ["group"]
            ),
            "drift_score": Gauge(
                "drift_score",
                "Model drift score",
                ["model"]
            ),
            "model_version": Gauge(
                "model_version",
                "Current model version",
                ["model"]
            ),
            
            # Resource Metrics
            "memory_usage": Gauge(
                "memory_usage",
                "Memory usage in bytes",
                ["component"]
            ),
            "cpu_usage": Gauge(
                "cpu_usage",
                "CPU usage percentage",
                ["component"]
            )
        }
        
        # Start Prometheus server
        try:
            start_http_server(self.config.get("port", 8000))
            self.logger.info("Prometheus server started")
        except Exception as e:
            self.logger.error(f"Failed to start Prometheus server: {str(e)}")
            raise MonitoringError(f"Failed to start Prometheus server: {str(e)}")
    
    def update_accuracy(self, model: str, accuracy: float) -> None:
        """Update model accuracy metric"""
        self.metrics["model_accuracy"].labels(model=model).set(accuracy)
    
    def update_latency(self, model: str, latency: float) -> None:
        """Update model latency metric"""
        self.metrics["model_latency"].labels(model=model).observe(latency)
    
    def increment_error(self, error_type: str) -> None:
        """Increment error counter"""
        self.metrics["error_count"].labels(type=error_type).inc()
    
    def increment_transaction(self, status: str) -> None:
        """Increment transaction counter"""
        self.metrics["transaction_count"].labels(status=status).inc()
    
    def update_bias(self, group: str, score: float) -> None:
        """Update bias score metric"""
        self.metrics["bias_score"].labels(group=group).set(score)
    
    def update_drift(self, model: str, score: float) -> None:
        """Update model drift score"""
        self.metrics["drift_score"].labels(model=model).set(score)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metric values"""
        return {
            "accuracy": {
                labels: gauge._value.get() 
                for labels, gauge in self.metrics["model_accuracy"]._metrics.items()
            },
            "latency": {
                labels: histogram._sum.get() 
                for labels, histogram in self.metrics["model_latency"]._metrics.items()
            },
            "errors": {
                labels: counter._value.get() 
                for labels, counter in self.metrics["error_count"]._metrics.items()
            },
            "transactions": {
                labels: counter._value.get() 
                for labels, counter in self.metrics["transaction_count"]._metrics.items()
            },
            "bias": {
                labels: gauge._value.get() 
                for labels, gauge in self.metrics["bias_score"]._metrics.items()
            },
            "drift": {
                labels: gauge._value.get() 
                for labels, gauge in self.metrics["drift_score"]._metrics.items()
            }
        }
    
    def validate_metrics(self) -> Dict[str, Any]:
        """Validate metrics against thresholds and return validation results"""
        metrics = self.get_metrics()
        thresholds = self.config["monitoring"]["alert_thresholds"]
        validation_results = {}
        
        # Validate error rate
        error_rate = metrics.get("error_rate", {})
        for model, rate in error_rate.items():
            if rate > thresholds["error_rate"]:
                validation_results[f"error_rate_{model}"] = {
                    "status": "exceeded",
                    "value": rate,
                    "threshold": thresholds["error_rate"]
                }
        
        # Validate response time
        latency = metrics.get("model_latency", {})
        for model, lat in latency.items():
            if lat > thresholds["response_time"]:
                validation_results[f"latency_{model}"] = {
                    "status": "exceeded",
                    "value": lat,
                    "threshold": thresholds["response_time"]
                }
        
        # Validate false positive rate
        fp_rate = metrics.get("false_positive_rate", {})
        for model, rate in fp_rate.items():
            if rate > thresholds["false_positive_rate"]:
                validation_results[f"false_positive_{model}"] = {
                    "status": "exceeded",
                    "value": rate,
                    "threshold": thresholds["false_positive_rate"]
                }
        
        # Validate false negative rate
        fn_rate = metrics.get("false_negative_rate", {})
        for model, rate in fn_rate.items():
            if rate > thresholds["false_negative_rate"]:
                validation_results[f"false_negative_{model}"] = {
                    "status": "exceeded",
                    "value": rate,
                    "threshold": thresholds["false_negative_rate"]
                }
        
        # Log validation results
        if validation_results:
            self.logger.warning(f"Metrics exceeded thresholds: {validation_results}")
        
        return validation_results
