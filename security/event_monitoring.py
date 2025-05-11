"""
Event Monitoring System

This module implements enterprise-grade event monitoring and alerting.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

class EventMonitorError(Exception):
    """Raised when event monitoring operations fail"""
    pass

class EventMonitor:
    """
    Enterprise-grade event monitoring system.
    
    Implements NIST SP 800-53 event monitoring requirements.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize event monitoring system.
        
        Args:
            config: Configuration containing:
                - log_all_events: Whether to log all events
                - alert_thresholds: Risk level thresholds for alerts
                - retention_period: Event retention period in days
                - monitoring_intervals: Monitoring check intervals
        """
        self.config = config
        
        # Monitoring parameters
        self.log_all_events = config.get("log_all_events", True)
        self.alert_thresholds = config.get("alert_thresholds", {
            "high_risk": 5,
            "medium_risk": 10,
            "low_risk": 20
        })
        self.retention_period = timedelta(days=config.get("retention_period", 30))
        self.monitoring_interval = timedelta(minutes=config.get("monitoring_interval_minutes", 5))
        
        # Event tracking
        self.events: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.alerts: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.risk_counts: Dict[str, int] = defaultdict(int)
        
    def log_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Log a security event.
        
        Args:
            event_type: Type of event (e.g., authentication, access)
            details: Event details including risk level and metadata
            
        Raises:
            EventMonitorError: If event logging fails
        """
        try:
            event = {
                "type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "details": details,
                "risk_level": details.get("risk_level", "low"),
                "source": details.get("source", "unknown")
            }
            
            # Add to event history
            self.events[event_type].append(event)
            
            # Update risk counts
            self.risk_counts[event_type] += 1
            
            # Check for alerts
            self._check_for_alerts(event)
            
            # Clean up old events
            self._cleanup_old_events()
            
        except Exception as e:
            logger.error(f"Failed to log event: {str(e)}")
            raise EventMonitorError(f"Failed to log event: {str(e)}")
    
    def _check_for_alerts(self, event: Dict[str, Any]) -> None:
        """Check if event triggers an alert."""
        event_type = event["type"]
        risk_level = event["risk_level"]
        
        # Check risk thresholds
        if risk_level == "high" and self.risk_counts[event_type] >= self.alert_thresholds["high_risk"]:
            self._generate_alert(event, "High risk threshold exceeded")
        elif risk_level == "medium" and self.risk_counts[event_type] >= self.alert_thresholds["medium_risk"]:
            self._generate_alert(event, "Medium risk threshold exceeded")
        elif risk_level == "low" and self.risk_counts[event_type] >= self.alert_thresholds["low_risk"]:
            self._generate_alert(event, "Low risk threshold exceeded")
    
    def _generate_alert(self, event: Dict[str, Any], reason: str) -> None:
        """Generate an alert for a security event."""
        alert = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "reason": reason,
            "severity": event["risk_level"],
            "alert_type": "security"
        }
        self.alerts[event["type"]].append(alert)
        
        # Log the alert
        logger.warning(f"Security alert generated: {json.dumps(alert)}")
    
    def _cleanup_old_events(self) -> None:
        """Remove events older than retention period."""
        current_time = datetime.utcnow()
        
        for event_type, events in self.events.items():
            self.events[event_type] = [
                e for e in events 
                if datetime.fromisoformat(e["timestamp"]) > current_time - self.retention_period
            ]
    
    def get_event_metrics(self) -> Dict[str, Any]:
        """Get current event monitoring metrics."""
        metrics = {
            "total_events": sum(len(events) for events in self.events.values()),
            "active_alerts": sum(len(alerts) for alerts in self.alerts.values()),
            "risk_counts": dict(self.risk_counts),
            "alert_thresholds": self.alert_thresholds,
            "retention_period": self.retention_period.days,
            "event_types": list(self.events.keys())
        }
        return metrics
    
    def get_alerts(self, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all alerts, optionally filtered by event type.
        
        Args:
            event_type: Optional event type to filter alerts
            
        Returns:
            List of alert dictionaries
        """
        if event_type:
            return self.alerts.get(event_type, [])
        return [alert for alerts in self.alerts.values() for alert in alerts]
    
    def get_events(self, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all events, optionally filtered by event type.
        
        Args:
            event_type: Optional event type to filter events
            
        Returns:
            List of event dictionaries
        """
        if event_type:
            return self.events.get(event_type, [])
        return [event for events in self.events.values() for event in events]
