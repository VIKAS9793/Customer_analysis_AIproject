from typing import Dict, Any
from datetime import datetime, timedelta

class SLAMonitoring:
    def __init__(self, config: Dict[str, Any], exporter=None):
        self.config = config
        self.exporter = exporter
        self.metrics = {}
        self.current_metrics = {}
        
        # Get SLA thresholds from monitoring config
        monitoring_config = config.get('monitoring', {})
        self.sla_thresholds = monitoring_config.get('sla_thresholds', {
            'min_availability': 0.99,
            'max_response_time': 2.0,
            'max_error_rate': 0.01,
            'max_false_positive_rate': 0.05,
            'max_false_negative_rate': 0.05
        })

    def record_request_metrics(self, request_data: Dict[str, Any]) -> None:
        """Record metrics for a single request."""
        timestamp = datetime.now().isoformat()
        endpoint = request_data.get('endpoint', 'unknown')
        
        if endpoint not in self.metrics:
            self.metrics[endpoint] = []
            
        self.metrics[endpoint].append({
            'timestamp': timestamp,
            'response_time': request_data.get('response_time', 0),
            'success': request_data.get('success', True),
            'accuracy': request_data.get('accuracy', 1.0)
        })

    def update_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update metrics in bulk."""
        timestamp = datetime.now().isoformat()
        
        # Record as a single request with all metrics
        self.record_request_metrics({
            'endpoint': 'system',
            'timestamp': timestamp,
            'response_time': metrics.get('response_time', 0),
            'success': (metrics.get('total_requests', 1) - metrics.get('error_count', 0)) / metrics.get('total_requests', 1),
            'accuracy': 1.0 - (metrics.get('error_count', 0) / metrics.get('total_requests', 1))
        })
        
        # Update exporter if available
        if self.exporter:
            if 'model_metrics' in metrics:
                for metric, value in metrics['model_metrics'].items():
                    if hasattr(self.exporter, f'update_{metric}'):
                        getattr(self.exporter, f'update_{metric}')('system', value)

        # Update current metrics
        self.current_metrics = metrics

    def check_sla_compliance(self) -> bool:
        """Check if current metrics meet SLA requirements."""
        # Check availability
        total_time = self.current_metrics.get('uptime', 0) + self.current_metrics.get('downtime', 0)
        if total_time > 0:
            availability = self.current_metrics.get('uptime', 0) / total_time
            if availability < self.sla_thresholds['min_availability']:
                self.exporter.update_error_rate('sla', 1.0)
                return False
        
        # Check response time
        if self.current_metrics.get('response_time', 0) > self.sla_thresholds['max_response_time']:
            self.exporter.update_error_rate('sla', 1.0)
            return False
        
        # Check error rate
        total_requests = self.current_metrics.get('total_requests', 0)
        if total_requests > 0:
            error_rate = self.current_metrics.get('error_count', 0) / total_requests
            if error_rate > self.sla_thresholds['max_error_rate']:
                self.exporter.update_error_rate('sla', error_rate)
                return False
        
        # Check model metrics
        model_metrics = self.current_metrics.get('model_metrics', {})
        if model_metrics.get('false_positive_rate', 0) > self.sla_thresholds['max_false_positive_rate']:
            self.exporter.update_error_rate('sla', model_metrics['false_positive_rate'])
            return False
        if model_metrics.get('false_negative_rate', 0) > self.sla_thresholds['max_false_negative_rate']:
            self.exporter.update_error_rate('sla', model_metrics['false_negative_rate'])
            return False
        
        # All checks passed
        self.exporter.update_error_rate('sla', 0.0)
        return True
