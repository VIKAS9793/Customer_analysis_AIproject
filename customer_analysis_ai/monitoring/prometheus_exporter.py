from typing import Dict, Any
from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry

class PrometheusExporter:
    def __init__(self, config: Dict[str, Any]):
        """Initialize the exporter."""
        self.config = config or {}
        self.registry = CollectorRegistry()
        
        # Define metrics
        self.request_counter = Counter(
            'customer_analysis_requests_total',
            'Total number of customer analysis requests',
            ['endpoint', 'status'],
            registry=self.registry
        )
        
        self.processing_time = Histogram(
            'customer_analysis_processing_seconds',
            'Time spent processing customer analysis requests',
            ['endpoint'],
            registry=self.registry
        )
        
        self.model_confidence = Gauge(
            'customer_analysis_model_confidence',
            'Confidence score of model predictions',
            ['model_type'],
            registry=self.registry
        )
        
        self.error_rate = Gauge(
            'customer_analysis_error_rate',
            'Error rate of model predictions',
            ['model_type'],
            registry=self.registry
        )
        
        self.model_accuracy = Gauge(
            'customer_analysis_model_accuracy',
            'Accuracy of model predictions',
            ['model_type'],
            registry=self.registry
        )
        
        self.model_drift = Gauge(
            'customer_analysis_model_drift',
            'Drift score of model predictions',
            ['model_type'],
            registry=self.registry
        )

    def record_request(self, endpoint: str, status: str) -> None:
        """Record a request."""
        self.request_counter.labels(endpoint=endpoint, status=status).inc()

    def record_processing_time(self, endpoint: str, duration: float) -> None:
        """Record request processing time."""
        self.processing_time.labels(endpoint=endpoint).observe(duration)

    def record_confidence(self, model_type: str, confidence: float) -> None:
        """Record model confidence."""
        self.model_confidence.labels(model_type=model_type).set(confidence)

    def update_error_rate(self, model_type: str, rate: float) -> None:
        """Update error rate metric."""
        self.error_rate.labels(model_type=model_type).set(rate)

    def update_drift(self, model_type: str, drift_score: float) -> None:
        """Update drift score for a model."""
        self.model_drift.labels(model_type=model_type).set(drift_score)
        
    def update_confidence(self, model_type: str, confidence: float) -> None:
        """Update model confidence score."""
        self.model_confidence.labels(model_type=model_type).set(confidence)

    def update_accuracy(self, model_type: str, accuracy: float) -> None:
        """Update model accuracy."""
        self.model_accuracy.labels(model_type=model_type).set(accuracy)

    def update_latency(self, model_type: str, latency: float) -> None:
        """Update model latency."""
        self.processing_time.labels(endpoint=model_type).observe(latency)

    def validate_metrics(self) -> Dict[str, bool]:
        """Validate all metrics against thresholds.
        Returns a dict of failed validations only.
        Empty dict means all validations passed.
        """
        thresholds = self.config.get('alert_thresholds', {})
        failed = {}
        
        # Check error rates
        for name, metric in self.error_rate._metrics.items():
            if float(metric._value.get()) > thresholds.get('error_rate', 0.01):
                failed['error_rate'] = False
                break
                
        # Check response times
        for name, metric in self.processing_time._metrics.items():
            if float(metric._sum.get()) > thresholds.get('response_time', 2.0):
                failed['response_time'] = False
                break
                
        # Check model confidence
        for name, metric in self.model_confidence._metrics.items():
            if float(metric._value.get()) < thresholds.get('model_confidence', 0.8):
                failed['model_confidence'] = False
                break
            
        return failed

    def get_metrics(self) -> Dict[str, float]:
        """Get current metric values."""
        metrics = {}
        # Handle Gauge metrics
        for metric in [self.error_rate, self.model_confidence, self.model_accuracy, self.model_drift]:
            metric_name = metric._name
            for labels, m in metric._metrics.items():
                key = f"{metric_name}{labels}"
                metrics[key] = float(m._value.get())
        
        # Handle Counter metrics
        metric_name = self.request_counter._name
        for labels, m in self.request_counter._metrics.items():
            key = f"{metric_name}{labels}"
            metrics[key] = float(m._value.get())
        
        # Handle Histogram metrics
        metric_name = self.processing_time._name
        for labels, m in self.processing_time._metrics.items():
            key = f"{metric_name}{labels}"
            metrics[key] = float(m._sum.get())
            
        return metrics
