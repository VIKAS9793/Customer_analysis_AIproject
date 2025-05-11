"""
Prometheus Metrics Exporter

This module implements Prometheus metrics collection and export for the FinConnectAI system.
"""

from typing import Dict, Any
import time
from prometheus_client import Counter, Histogram, Gauge, Summary, start_http_server
import logging

class MetricsExporter:
    def __init__(self, config: Dict[str, Any]):
        """Initialize metrics exporter with configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize metrics
        self._init_request_metrics()
        self._init_model_metrics()
        self._init_system_metrics()
        self._init_business_metrics()
        
        # Start metrics server
        self.start_server()
        
    def _init_request_metrics(self):
        """Initialize request-related metrics"""
        self.request_counter = Counter(
            'customer_ai_requests_total',
            'Total number of API requests',
            ['endpoint', 'method', 'status']
        )
        
        self.request_latency = Histogram(
            'customer_ai_request_latency_seconds',
            'Request latency in seconds',
            ['endpoint'],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0)
        )
        
        self.request_in_progress = Gauge(
            'customer_ai_requests_in_progress',
            'Number of requests currently being processed',
            ['endpoint']
        )
        
    def _init_model_metrics(self):
        """Initialize model-related metrics"""
        self.model_prediction_latency = Histogram(
            'customer_ai_model_prediction_latency_seconds',
            'Model prediction latency in seconds',
            ['model_version']
        )
        
        self.model_accuracy = Gauge(
            'customer_ai_model_accuracy',
            'Model accuracy score',
            ['model_version']
        )
        
        self.prediction_errors = Counter(
            'customer_ai_prediction_errors_total',
            'Total number of prediction errors',
            ['error_type', 'model_version']
        )
        
    def _init_system_metrics(self):
        """Initialize system-related metrics"""
        self.system_memory_usage = Gauge(
            'customer_ai_memory_usage_bytes',
            'Current memory usage in bytes'
        )
        
        self.system_cpu_usage = Gauge(
            'customer_ai_cpu_usage_percent',
            'Current CPU usage percentage'
        )
        
        self.system_disk_usage = Gauge(
            'customer_ai_disk_usage_bytes',
            'Current disk usage in bytes',
            ['mount_point']
        )
        
    def _init_business_metrics(self):
        """Initialize business-related metrics"""
        self.customer_segments = Gauge(
            'customer_ai_customer_segments',
            'Number of customers in each segment',
            ['segment']
        )
        
        self.analysis_accuracy = Summary(
            'customer_ai_analysis_accuracy',
            'Customer analysis accuracy score'
        )
        
        self.business_value = Counter(
            'customer_ai_business_value',
            'Estimated business value generated',
            ['metric_type']
        )
        
    def start_server(self):
        """Start the metrics server"""
        try:
            port = self.config.get("metrics_port", 9090)
            start_http_server(port)
            self.logger.info(f"Metrics server started on port {port}")
        except Exception as e:
            self.logger.error(f"Failed to start metrics server: {str(e)}")
            raise
            
    def track_request(self, endpoint: str, method: str, status: int, duration: float):
        """Track API request metrics"""
        try:
            self.request_counter.labels(endpoint=endpoint, method=method, status=status).inc()
            self.request_latency.labels(endpoint=endpoint).observe(duration)
        except Exception as e:
            self.logger.error(f"Failed to track request metrics: {str(e)}")
            
    def track_model_prediction(self, model_version: str, duration: float, error_type: str = None):
        """Track model prediction metrics"""
        try:
            self.model_prediction_latency.labels(model_version=model_version).observe(duration)
            
            if error_type:
                self.prediction_errors.labels(
                    error_type=error_type,
                    model_version=model_version
                ).inc()
        except Exception as e:
            self.logger.error(f"Failed to track model prediction metrics: {str(e)}")
            
    def update_model_accuracy(self, model_version: str, accuracy: float):
        """Update model accuracy metrics"""
        try:
            self.model_accuracy.labels(model_version=model_version).set(accuracy)
        except Exception as e:
            self.logger.error(f"Failed to update model accuracy: {str(e)}")
            
    def update_system_metrics(self, memory_usage: float, cpu_usage: float, disk_usage: Dict[str, float]):
        """Update system metrics"""
        try:
            self.system_memory_usage.set(memory_usage)
            self.system_cpu_usage.set(cpu_usage)
            
            for mount_point, usage in disk_usage.items():
                self.system_disk_usage.labels(mount_point=mount_point).set(usage)
        except Exception as e:
            self.logger.error(f"Failed to update system metrics: {str(e)}")
            
    def update_business_metrics(self, segment_counts: Dict[str, int], analysis_accuracy: float, value_generated: Dict[str, float]):
        """Update business metrics"""
        try:
            # Update segment counts
            for segment, count in segment_counts.items():
                self.customer_segments.labels(segment=segment).set(count)
                
            # Update analysis accuracy
            self.analysis_accuracy.observe(analysis_accuracy)
            
            # Update business value
            for metric_type, value in value_generated.items():
                self.business_value.labels(metric_type=metric_type).inc(value)
        except Exception as e:
            self.logger.error(f"Failed to update business metrics: {str(e)}")
            
    def track_request_in_progress(self, endpoint: str):
        """Track requests in progress using context manager"""
        class RequestTracker:
            def __init__(self, gauge, endpoint):
                self.gauge = gauge
                self.endpoint = endpoint
                
            def __enter__(self):
                self.gauge.labels(endpoint=self.endpoint).inc()
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.gauge.labels(endpoint=self.endpoint).dec()
                
        return RequestTracker(self.request_in_progress, endpoint)
        
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot"""
        return {
            "request_metrics": {
                "total_requests": self.request_counter._value.sum(),
                "average_latency": self.request_latency._sum.sum() / self.request_latency._count.sum()
                if self.request_latency._count.sum() > 0 else 0
            },
            "model_metrics": {
                "average_prediction_latency": self.model_prediction_latency._sum.sum() / 
                    self.model_prediction_latency._count.sum()
                    if self.model_prediction_latency._count.sum() > 0 else 0,
                "total_errors": self.prediction_errors._value.sum()
            },
            "system_metrics": {
                "memory_usage": self.system_memory_usage._value.get(),
                "cpu_usage": self.system_cpu_usage._value.get()
            },
            "business_metrics": {
                "total_value_generated": self.business_value._value.sum()
            }
        }
