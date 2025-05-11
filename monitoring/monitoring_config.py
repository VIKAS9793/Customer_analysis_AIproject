from typing import Dict, Any, List, Optional

# Monitoring System Configuration
MONITORING_CONFIG = {
    # Real-time Monitoring
    "real_time_monitoring": {
        "enabled": True,
        "interval": 60,  # seconds
        "retention_period": "30d",
        "metrics": [
            "performance",
            "error_rate",
            "latency",
            "drift_detection"
        ]
    },
    
    # Dashboard Integration
    "dashboard": {
        "tool": "Prometheus",
        "metrics_interval": 60,  # seconds
        "endpoints": {
            "prometheus": "/metrics",
            "health": "/health",
            "status": "/status"
        },
        "exporters": [
            "node_exporter",
            "process_exporter",
            "blackbox_exporter"
        ]
    },
    
    # Grafana Integration
    "grafana": {
        "enabled": True,
        "dashboards": [
            "system_overview",
            "security_metrics",
            "compliance_status",
            "api_performance",
            "model_performance"
        ],
        "refresh_interval": "1m",
        "retention_period": "90d",
        "alerts_enabled": True
    },
    
    # Alert System
    "alerts": {
        "enabled": True,
        "channels": [
            "email",
            "slack",
            "webhook",
            "pagerduty"
        ],
        "severity_levels": [
            "critical",
            "high",
            "medium",
            "low",
            "info"
        ],
        "grouping": True,
        "deduplication": True,
        "throttling": {
            "enabled": True,
            "window": "1h",
            "max_alerts": 10
        }
    },
    
    # Alert Thresholds
    "thresholds": {
        "error_rate": 0.01,
        "response_time": 2.0,  # seconds
        "false_positive_rate": 0.05,
        "false_negative_rate": 0.02,
        "cpu_usage": 0.8,  # 80%
        "memory_usage": 0.8,  # 80%
        "disk_usage": 0.8,  # 80%
        "api_request_rate": 100  # requests per second
    },
    
    # SLA Monitoring
    "sla": {
        "enabled": True,
        "targets": {
            "availability": 0.999,  # 99.9%
            "response_time": 1.0,  # second
            "error_rate": 0.001,  # 0.1%
            "incident_response_time": {
                "critical": 15,  # minutes
                "high": 60,  # minutes
                "medium": 240,  # minutes
                "low": 1440  # minutes (24 hours)
            }
        },
        "reporting": {
            "frequency": "monthly",
            "format": "pdf",
            "recipients": ["compliance_officer", "security_officer", "operations_team"]
        }
    },
    
    # Performance Metrics
    "performance_metrics": {
        "system": [
            "cpu_usage",
            "memory_usage",
            "disk_usage",
            "network_bandwidth"
        ],
        "application": [
            "request_count",
            "error_count",
            "response_time",
            "queue_depth"
        ],
        "model": [
            "inference_time",
            "prediction_accuracy",
            "false_positive_rate",
            "false_negative_rate",
            "drift_score"
        ]
    },
    
    # Health Checks
    "health_checks": {
        "endpoints": [
            "api",
            "database",
            "model_service",
            "authentication",
            "storage"
        ],
        "interval": 30,  # seconds
        "timeout": 5,  # seconds
        "retries": 3
    }
}
