from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import json
from .security_monitor import SecurityMonitor
from .risk_assessment import RiskAssessment

class ThreatDetector:
    """
    Enterprise-grade threat detection system.
    
    Implements real-time threat detection, anomaly detection,
    and risk assessment following NIST SP 800-61 guidelines.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize threat detection system.
        
        Args:
            config: Configuration containing:
                - detection_rules: Threat detection rules
                - anomaly_thresholds: Anomaly detection thresholds
                - risk_assessment: Risk assessment parameters
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.security_monitor = SecurityMonitor(config)
        self.risk_assessment = RiskAssessment(config)
        
        # Detection rules
        self.detection_rules = config.get("detection_rules", {
            "login_attempts": {
                "threshold": 5,
                "time_window": 60,
                "risk_level": "high"
            },
            "geo_anomalies": {
                "threshold": 1000,
                "time_window": 3600,
                "risk_level": "medium"
            },
            "rate_limiting": {
                "threshold": 1000,
                "time_window": 60,
                "risk_level": "high"
            }
        })
        
        # Anomaly detection
        self.anomaly_thresholds = config.get("anomaly_thresholds", {
            "login_rate": 5,
            "request_rate": 1000,
            "geo_velocity": 1000,
            "pattern_changes": 0.5
        })
    
    def detect_threats(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect potential threats in security events.
        
        Args:
            event: Security event to analyze
            
        Returns:
            List of detected threats with details
        """
        try:
            threats = []
            
            # Check detection rules
            for rule_name, rule in self.detection_rules.items():
                if self._check_rule(event, rule):
                    threat = {
                        "type": rule_name,
                        "risk_level": rule["risk_level"],
                        "details": event,
                        "timestamp": datetime.now().isoformat()
                    }
                    threats.append(threat)
                    
            # Perform anomaly detection
            anomalies = self._detect_anomalies(event)
            threats.extend(anomalies)
            
            # Perform risk assessment
            risk_level = self.risk_assessment.evaluate_risk(event)
            if risk_level != "low":
                threat = {
                    "type": "risk_assessment",
                    "risk_level": risk_level,
                    "details": event,
                    "timestamp": datetime.now().isoformat()
                }
                threats.append(threat)
            
            return threats
            
        except Exception as e:
            self.logger.error(f"Threat detection failed: {str(e)}")
            raise ThreatDetectionError(f"Failed to detect threats: {str(e)}") from e
    
    def _check_rule(self, event: Dict[str, Any], rule: Dict[str, Any]) -> bool:
        """Check if event matches threat detection rule"""
        try:
            # Get events within time window
            events = self.security_monitor.get_events(
                event_type=event["type"],
                time_window=rule["time_window"]
            )
            
            # Check threshold
            if len(events) >= rule["threshold"]:
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Rule check failed: {str(e)}")
            raise RuleCheckError(f"Failed to check rule: {str(e)}") from e
    
    def _detect_anomalies(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies in security events"""
        try:
            anomalies = []
            
            # Check login rate
            if event["type"] == "login":
                rate = self.security_monitor.get_rate(
                    event_type="login",
                    time_window=60
                )
                if rate > self.anomaly_thresholds["login_rate"]:
                    anomaly = {
                        "type": "login_rate_anomaly",
                        "details": {
                            "rate": rate,
                            "threshold": self.anomaly_thresholds["login_rate"]
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                    anomalies.append(anomaly)
            
            # Check request rate
            if event["type"] == "request":
                rate = self.security_monitor.get_rate(
                    event_type="request",
                    time_window=60
                )
                if rate > self.anomaly_thresholds["request_rate"]:
                    anomaly = {
                        "type": "request_rate_anomaly",
                        "details": {
                            "rate": rate,
                            "threshold": self.anomaly_thresholds["request_rate"]
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                    anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {str(e)}")
            raise AnomalyDetectionError(f"Failed to detect anomalies: {str(e)}") from e

class ThreatDetectionError(Exception):
    """Raised when threat detection fails"""
    pass

class RuleCheckError(Exception):
    """Raised when rule check fails"""
    pass

class AnomalyDetectionError(Exception):
    """Raised when anomaly detection fails"""
    pass
