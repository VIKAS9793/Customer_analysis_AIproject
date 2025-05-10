from datetime import datetime
from typing import Dict, Any, List

class MonitoringAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics = []

    def record_metric(self, metric_name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Record a metric value with optional labels."""
        self.metrics.append({
            'name': metric_name,
            'value': value,
            'labels': labels or {},
            'timestamp': datetime.now().isoformat()
        })

    def get_metrics(self, metric_name: str = None) -> List[Dict[str, Any]]:
        """Get recorded metrics, optionally filtered by name."""
        if metric_name is None:
            return self.metrics
            
        return [
            m for m in self.metrics 
            if m['name'] == metric_name
        ]

    def clear_metrics(self) -> None:
        """Clear all recorded metrics."""
        self.metrics = []
