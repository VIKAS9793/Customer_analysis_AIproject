"""
Metrics and Monitoring - Handles metrics collection and monitoring.

This module provides functionality for collecting and reporting metrics
about the FinConnectAI framework's performance and usage.
"""

import logging
import time
from functools import wraps
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class MetricsManager:
    """
    Manager for metrics collection and monitoring.

    This class provides methods for collecting, aggregating, and reporting
    metrics about the FinConnectAI framework's performance and usage.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize a metrics manager.

        Args:
            config: Configuration for the manager
        """
        self.config = config
        self.metrics_enabled = config.get("metrics_enabled", True)
        self.metrics_interval = config.get("metrics_interval", 60)  # seconds
        self.metrics_storage = {}
        self.last_report_time = time.time()

        # Initialize counters and gauges
        self._initialize_metrics()

        logger.info("Initialized metrics manager")

    def _initialize_metrics(self) -> None:
        """Initialize metrics counters and gauges."""
        # Initialize counters and gauges
        self.metrics_storage["request_count"] = 0
        self.metrics_storage["request_success_count"] = 0
        self.metrics_storage["request_error_count"] = 0
        self.metrics_storage["request_latency"] = []

        # Initialize decision metrics
        self.metrics_storage["total_decisions"] = 0
        self.metrics_storage["false_positives"] = 0
        self.metrics_storage["false_negatives"] = 0
        self.metrics_storage["true_positives"] = 0
        self.metrics_storage["true_negatives"] = 0

        # Initialize thresholds
        self.false_positive_threshold = config.get("alert_thresholds", {}).get("false_positive_rate", 0.05)
        self.false_negative_threshold = config.get("alert_thresholds", {}).get("false_negative_rate", 0.02)

        # Initialize last alert times
        self.last_false_positive_alert = 0
        self.last_false_negative_alert = 0

        # Request metrics
        self.metrics_storage["task_count"] = 0
        self.metrics_storage["task_success_count"] = 0
        self.metrics_storage["task_error_count"] = 0
        self.metrics_storage["task_latency"] = []

        # Model metrics
        self.metrics_storage["model_call_count"] = 0
        self.metrics_storage["model_token_count"] = 0
        self.metrics_storage["model_latency"] = []

        # Memory metrics
        self.metrics_storage["memory_store_count"] = 0
        self.metrics_storage["memory_retrieve_count"] = 0
        self.metrics_storage["memory_search_count"] = 0

        # Knowledge metrics
        self.metrics_storage["knowledge_search_count"] = 0
        self.metrics_storage["knowledge_add_count"] = 0

        # Action metrics
        self.metrics_storage["action_count"] = 0
        self.metrics_storage["action_success_count"] = 0
        self.metrics_storage["action_error_count"] = 0

        # Safety metrics
        self.metrics_storage["hallucination_detected_count"] = 0
        self.metrics_storage["bias_detected_count"] = 0
        self.metrics_storage["pii_detected_count"] = 0

    def record_request(self, endpoint: str, status_code: int, latency: float) -> None:
        """
        Record a request metric.

        Args:
            endpoint: The API endpoint
            status_code: The HTTP status code
            latency: The request latency in seconds
        """
        if not self.metrics_enabled:
            return

        self.metrics_storage["request_count"] += 1
        self.metrics_storage["request_latency"].append(latency)

        if 200 <= status_code < 300:
            self.metrics_storage["request_success_count"] += 1
        else:
            self.metrics_storage["request_error_count"] += 1

        # Check if it's time to report metrics
        self._check_report_metrics()

    def record_task(self, task_type: str, success: bool, latency: float) -> None:
        """
        Record a task metric.

        Args:
            task_type: The type of task
            success: Whether the task was successful
            latency: The task latency in seconds
        """
        if not self.metrics_enabled:
            return

        self.metrics_storage["task_count"] += 1
        self.metrics_storage["task_latency"].append(latency)

        if success:
            self.metrics_storage["task_success_count"] += 1
        else:
            self.metrics_storage["task_error_count"] += 1

        # Check if it's time to report metrics
        self._check_report_metrics()

    def record_model_call(self, model: str, token_count: int, latency: float) -> None:
        """
        Record a model call metric.

        Args:
            model: The model name
            token_count: The number of tokens
            latency: The model call latency in seconds
        """
        if not self.metrics_enabled:
            return

        self.metrics_storage["model_call_count"] += 1
        self.metrics_storage["model_token_count"] += token_count
        self.metrics_storage["model_latency"].append(latency)

        # Check if it's time to report metrics
        self._check_report_metrics()

    def record_memory_operation(self, operation: str) -> None:
        """
        Record a memory operation metric.

        Args:
            operation: The memory operation (store, retrieve, search)
        """
        if not self.metrics_enabled:
            return

        if operation == "store":
            self.metrics_storage["memory_store_count"] += 1
        elif operation == "retrieve":
            self.metrics_storage["memory_retrieve_count"] += 1
        elif operation == "search":
            self.metrics_storage["memory_search_count"] += 1

        # Check if it's time to report metrics
        self._check_report_metrics()

    def record_knowledge_operation(self, operation: str) -> None:
        """
        Record a knowledge operation metric.

        Args:
            operation: The knowledge operation (search, add)
        """
        if not self.metrics_enabled:
            return

        if operation == "search":
            self.metrics_storage["knowledge_search_count"] += 1
        elif operation == "add":
            self.metrics_storage["knowledge_add_count"] += 1

        # Check if it's time to report metrics
        self._check_report_metrics()

    def record_action(self, action_type: str, success: bool) -> None:
        """
        Record an action metric.

        Args:
            action_type: The type of action
            success: Whether the action was successful
        """
        if not self.metrics_enabled:
            return

        self.metrics_storage["action_count"] += 1

        if success:
            self.metrics_storage["action_success_count"] += 1
        else:
            self.metrics_storage["action_error_count"] += 1

        # Check if it's time to report metrics
        self._check_report_metrics()

    def record_safety_event(self, event_type: str) -> None:
        """
        Record a safety event metric.

        Args:
            event_type: The type of safety event (hallucination, bias, pii)
        """
        if not self.metrics_enabled:
            return

        if event_type == "hallucination":
            self.metrics_storage["hallucination_detected_count"] += 1
        elif event_type == "bias":
            self.metrics_storage["bias_detected_count"] += 1
        elif event_type == "pii":
            self.metrics_storage["pii_detected_count"] += 1

        # Check if it's time to report metrics
        self._check_report_metrics()

    def _check_report_metrics(self) -> None:
        """Check if it's time to report metrics and do so if needed."""
        current_time = time.time()
        if current_time - self.last_report_time >= self.metrics_interval:
            self.report_metrics()
            self.last_report_time = current_time

    def report_metrics(self) -> Dict[str, Any]:
        """
        Report current metrics.

        Returns:
            Dictionary with current metrics
        """
        if not self.metrics_enabled:
            return {}

        logger.info("Reporting metrics")

        # Calculate derived metrics
        metrics = self._calculate_derived_metrics()

        # Log metrics
        for category, values in metrics.items():
            for metric, value in values.items():
                logger.info(f"Metric: {category}.{metric} = {value}")

        # Reset certain metrics
        self._reset_metrics()

        return metrics

    def _calculate_derived_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Calculate derived metrics from raw metrics.

        Returns:
            Dictionary with derived metrics
        """
        metrics = {
            "request": {
                "total": self.metrics_storage["request_count"],
                "success": self.metrics_storage["request_success_count"],
                "error": self.metrics_storage["request_error_count"],
            },
            "task": {
                "total": self.metrics_storage["task_count"],
                "success": self.metrics_storage["task_success_count"],
                "error": self.metrics_storage["task_error_count"],
            },
            "model": {
                "calls": self.metrics_storage["model_call_count"],
                "tokens": self.metrics_storage["model_token_count"],
            },
            "memory": {
                "store": self.metrics_storage["memory_store_count"],
                "retrieve": self.metrics_storage["memory_retrieve_count"],
                "search": self.metrics_storage["memory_search_count"],
            },
            "knowledge": {
                "search": self.metrics_storage["knowledge_search_count"],
                "add": self.metrics_storage["knowledge_add_count"],
            },
            "action": {
                "total": self.metrics_storage["action_count"],
                "success": self.metrics_storage["action_success_count"],
                "error": self.metrics_storage["action_error_count"],
            },
            "safety": {
                "hallucination": self.metrics_storage["hallucination_detected_count"],
                "bias": self.metrics_storage["bias_detected_count"],
                "pii": self.metrics_storage["pii_detected_count"],
            },
        }

        # Calculate success rates
        if metrics["request"]["total"] > 0:
            metrics["request"]["success_rate"] = (
                metrics["request"]["success"] / metrics["request"]["total"]
            )

        if metrics["task"]["total"] > 0:
            metrics["task"]["success_rate"] = metrics["task"]["success"] / metrics["task"]["total"]

        if metrics["action"]["total"] > 0:
            metrics["action"]["success_rate"] = (
                metrics["action"]["success"] / metrics["action"]["total"]
            )

        # Calculate average latencies
        if self.metrics_storage["request_latency"]:
            metrics["request"]["avg_latency"] = sum(self.metrics_storage["request_latency"]) / len(
                self.metrics_storage["request_latency"]
            )
            metrics["request"]["max_latency"] = max(self.metrics_storage["request_latency"])
            metrics["request"]["min_latency"] = min(self.metrics_storage["request_latency"])

        if self.metrics_storage["task_latency"]:
            metrics["task"]["avg_latency"] = sum(self.metrics_storage["task_latency"]) / len(
                self.metrics_storage["task_latency"]
            )
            metrics["task"]["max_latency"] = max(self.metrics_storage["task_latency"])
            metrics["task"]["min_latency"] = min(self.metrics_storage["task_latency"])

        if self.metrics_storage["model_latency"]:
            metrics["model"]["avg_latency"] = sum(self.metrics_storage["model_latency"]) / len(
                self.metrics_storage["model_latency"]
            )
            metrics["model"]["max_latency"] = max(self.metrics_storage["model_latency"])
            metrics["model"]["min_latency"] = min(self.metrics_storage["model_latency"])

        # Calculate average tokens per call
        if metrics["model"]["calls"] > 0:
            metrics["model"]["avg_tokens_per_call"] = (
                metrics["model"]["tokens"] / metrics["model"]["calls"]
            )

        return metrics

    def _reset_metrics(self) -> None:
        """Reset metrics that should be reset after reporting."""
        # Reset latency lists
        self.metrics_storage["request_latency"] = []
        self.metrics_storage["task_latency"] = []
        self.metrics_storage["model_latency"] = []

        # Other metrics are cumulative and not reset


def timed_execution(metric_manager: Optional[MetricsManager] = None, metric_type: str = "task"):
    """
    Decorator for timing function execution and recording metrics.

    Args:
        metric_manager: Optional metrics manager to record metrics
        metric_type: Type of metric to record (task, model, request)

    Returns:
        Decorator function
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                success = False
                raise
            finally:
                end_time = time.time()
                latency = end_time - start_time

                if metric_manager:
                    if metric_type == "task":
                        metric_manager.record_task(func.__name__, success, latency)
                    elif metric_type == "model":
                        token_count = kwargs.get("token_count", 0)
                        metric_manager.record_model_call(func.__name__, token_count, latency)
                    elif metric_type == "request":
                        status_code = 200 if success else 500
                        metric_manager.record_request(func.__name__, status_code, latency)

        return wrapper

    return decorator
