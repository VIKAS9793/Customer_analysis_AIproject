from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from .security_events import SecurityEvent, SecurityEventSeverity
from .audit_trail import AuditTrail
from .risk_assessment import RiskAssessment

class SecurityMetrics:
    """
    Enterprise-grade security metrics collection and analysis.
    
    Implements NIST SP 800-55 compliant security metrics.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize security metrics system.
        
        Args:
            config: Configuration containing:
                - collection_interval: Metrics collection interval
                - retention_period: Metrics retention period
                - thresholds: Alert thresholds
                - risk_assessment: Risk assessment parameters
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.audit_trail = AuditTrail(config)
        self.risk_assessment = RiskAssessment(config)
        
        # Initialize metrics storage
        self.metrics = {
            "authentication": defaultdict(int),
            "authorization": defaultdict(int),
            "data_access": defaultdict(int),
            "security_violations": defaultdict(int),
            "risk_events": defaultdict(int),
            "audit_events": defaultdict(int)
        }
        
        # Load thresholds
        self.thresholds = self._load_thresholds()
        
    def _load_thresholds(self) -> Dict[str, Any]:
        """Load security metrics thresholds from configuration"""
        try:
            thresholds = self.config.get("thresholds", {
                "authentication_failures": {
                    "count": 5,
                    "time_window": 60,
                    "severity": SecurityEventSeverity.HIGH
                },
                "authorization_failures": {
                    "count": 10,
                    "time_window": 60,
                    "severity": SecurityEventSeverity.MEDIUM
                },
                "security_violations": {
                    "count": 1,
                    "time_window": 300,
                    "severity": SecurityEventSeverity.CRITICAL
                },
                "risk_events": {
                    "count": 5,
                    "time_window": 3600,
                    "severity": SecurityEventSeverity.HIGH
                }
            })
            return thresholds
            
        except Exception as e:
            self.logger.error(f"Failed to load thresholds: {str(e)}")
            raise MetricThresholdError(f"Failed to load thresholds: {str(e)}") from e
    
    def collect_metrics(self) -> Dict[str, Any]:
        """
        Collect security metrics.
        
        Returns:
            Dictionary of collected metrics
            
        Raises:
            MetricCollectionError: If metric collection fails
        """
        try:
            # Get events from audit trail
            events = self.audit_trail.get_events(
                time_window=self.config["collection_interval"]
            )
            
            # Process events
            for event in events:
                self._process_event(event)
            
            # Calculate metrics
            metrics = self._calculate_metrics()
            
            # Check thresholds and raise alerts
            self._check_thresholds(metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Metric collection failed: {str(e)}")
            raise MetricCollectionError(f"Failed to collect metrics: {str(e)}") from e
    
    def _process_event(self, event: Dict[str, Any]) -> None:
        """Process individual security event"""
        try:
            event_type = event["event_type"]
            severity = SecurityEventSeverity(event["severity"])
            
            # Increment appropriate counters
            if event_type == "authentication":
                self.metrics["authentication"][severity] += 1
            elif event_type == "authorization":
                self.metrics["authorization"][severity] += 1
            elif event_type == "data_access":
                self.metrics["data_access"][severity] += 1
            elif event_type == "security_violation":
                self.metrics["security_violations"][severity] += 1
            elif event_type == "risk_detection":
                self.metrics["risk_events"][severity] += 1
            elif event_type == "audit":
                self.metrics["audit_events"][severity] += 1
                
        except Exception as e:
            self.logger.error(f"Failed to process event: {str(e)}")
            raise EventProcessingError(f"Failed to process event: {str(e)}") from e
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate aggregated metrics"""
        try:
            metrics = {
                "authentication": {
                    "success": self.metrics["authentication"][SecurityEventSeverity.LOW],
                    "failure": sum(
                        self.metrics["authentication"][severity]
                        for severity in [SecurityEventSeverity.MEDIUM, 
                                        SecurityEventSeverity.HIGH,
                                        SecurityEventSeverity.CRITICAL]
                    )
                },
                "authorization": {
                    "success": self.metrics["authorization"][SecurityEventSeverity.LOW],
                    "failure": sum(
                        self.metrics["authorization"][severity]
                        for severity in [SecurityEventSeverity.MEDIUM, 
                                        SecurityEventSeverity.HIGH,
                                        SecurityEventSeverity.CRITICAL]
                    )
                },
                "data_access": {
                    "total": sum(self.metrics["data_access"][severity] 
                               for severity in SecurityEventSeverity)
                },
                "security_violations": {
                    "total": sum(self.metrics["security_violations"][severity] 
                                for severity in SecurityEventSeverity)
                },
                "risk_events": {
                    "total": sum(self.metrics["risk_events"][severity] 
                               for severity in SecurityEventSeverity)
                },
                "audit_events": {
                    "total": sum(self.metrics["audit_events"][severity] 
                               for severity in SecurityEventSeverity)
                }
            }
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to calculate metrics: {str(e)}")
            raise MetricCalculationError(f"Failed to calculate metrics: {str(e)}") from e
    
    def _check_thresholds(self, metrics: Dict[str, Any]) -> None:
        """Check if any metrics exceed configured thresholds"""
        try:
            # Check authentication failures
            if metrics["authentication"]["failure"] >= self.thresholds["authentication_failures"]["count"]:
                self._raise_alert(
                    "authentication_failures",
                    metrics["authentication"]["failure"]
                )
            
            # Check authorization failures
            if metrics["authorization"]["failure"] >= self.thresholds["authorization_failures"]["count"]:
                self._raise_alert(
                    "authorization_failures",
                    metrics["authorization"]["failure"]
                )
            
            # Check security violations
            if metrics["security_violations"]["total"] >= self.thresholds["security_violations"]["count"]:
                self._raise_alert(
                    "security_violations",
                    metrics["security_violations"]["total"]
                )
            
            # Check risk events
            if metrics["risk_events"]["total"] >= self.thresholds["risk_events"]["count"]:
                self._raise_alert(
                    "risk_events",
                    metrics["risk_events"]["total"]
                )
                
        except Exception as e:
            self.logger.error(f"Failed to check thresholds: {str(e)}")
            raise ThresholdCheckError(f"Failed to check thresholds: {str(e)}") from e
    
    def _raise_alert(self, alert_type: str, value: int) -> None:
        """Raise security alert when threshold is exceeded"""
        try:
            threshold = self.thresholds[alert_type]
            self.audit_trail.log_event(
                "security_alert",
                {
                    "type": alert_type,
                    "value": value,
                    "threshold": threshold["count"],
                    "severity": threshold["severity"].value,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to raise alert: {str(e)}")
            raise AlertError(f"Failed to raise alert: {str(e)}") from e

class MetricCollectionError(Exception):
    """Raised when metric collection fails"""
    pass

class MetricThresholdError(Exception):
    """Raised when threshold loading fails"""
    pass

class EventProcessingError(Exception):
    """Raised when event processing fails"""
    pass

class MetricCalculationError(Exception):
    """Raised when metric calculation fails"""
    pass

class ThresholdCheckError(Exception):
    """Raised when threshold checking fails"""
    pass

class AlertError(Exception):
    """Raised when alert generation fails"""
    pass
