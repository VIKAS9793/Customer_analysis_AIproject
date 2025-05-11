"""
Risk Assessment System

This module implements enterprise-grade risk assessment for security events.
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

class RiskAssessmentError(Exception):
    """Raised when risk assessment operations fail"""
    pass

class RiskAssessment:
    """
    Enterprise-grade risk assessment system.
    
    Implements OWASP risk assessment guidelines and NIST SP 800-63B requirements.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize risk assessment system.
        
        Args:
            config: Configuration containing:
                - max_failed_attempts: Maximum allowed failed attempts
                - lockout_duration_minutes: Duration of lockout after max attempts
                - ip_whitelist: List of whitelisted IP addresses
                - ip_blacklist: List of blacklisted IP addresses
                - risk_thresholds: Risk level thresholds
        """
        self.config = config
        
        # Security parameters
        self.max_failed_attempts = config.get("max_failed_attempts", 5)
        self.lockout_duration = timedelta(minutes=config.get("lockout_duration_minutes", 30))
        self.ip_whitelist = config.get("ip_whitelist", [])
        self.ip_blacklist = config.get("ip_blacklist", [])
        self.risk_thresholds = config.get("risk_thresholds", {
            "low": 0.3,
            "medium": 0.7,
            "high": 0.9
        })
        
        # State tracking
        self.failed_attempts: Dict[str, int] = defaultdict(int)
        self.locked_out: Dict[str, datetime] = {}
        self.last_access: Dict[str, datetime] = {}
        
    def evaluate_session(self, user_id: str, user_data: Dict[str, Any]) -> str:
        """
        Evaluate session risk level based on multiple factors.
        
        Args:
            user_id: Unique identifier for the user
            user_data: User-specific data including IP and metadata
            
        Returns:
            Risk level: "low", "medium", or "high"
            
        Raises:
            RiskAssessmentError: If risk assessment fails
        """
        try:
            # Check if user is locked out
            if user_id in self.locked_out:
                if datetime.utcnow() < self.locked_out[user_id]:
                    return "high"
                else:
                    del self.locked_out[user_id]
            
            # Check IP restrictions
            ip = user_data.get("ip_address")
            if ip in self.ip_blacklist:
                return "high"
                
            if self.ip_whitelist and ip not in self.ip_whitelist:
                return "medium"
            
            # Check failed attempts
            if user_id in self.failed_attempts:
                if self.failed_attempts[user_id] >= self.max_failed_attempts:
                    self.locked_out[user_id] = datetime.utcnow() + self.lockout_duration
                    return "high"
            
            # Check access patterns
            if user_id in self.last_access:
                time_since_last = datetime.utcnow() - self.last_access[user_id]
                if time_since_last.total_seconds() < 60:  # Multiple attempts in 1 minute
                    self.failed_attempts[user_id] += 1
                    return "medium"
            
            # Update last access
            self.last_access[user_id] = datetime.utcnow()
            
            # Calculate risk score based on various factors
            risk_score = self._calculate_risk_score(user_data)
            
            # Determine risk level
            if risk_score >= self.risk_thresholds["high"]:
                return "high"
            elif risk_score >= self.risk_thresholds["medium"]:
                return "medium"
            return "low"
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {str(e)}")
            raise RiskAssessmentError(f"Failed to evaluate risk: {str(e)}")
    
    def record_failed_attempt(self, user_id: str) -> None:
        """Record a failed authentication attempt."""
        self.failed_attempts[user_id] += 1
        if self.failed_attempts[user_id] >= self.max_failed_attempts:
            self.locked_out[user_id] = datetime.utcnow() + self.lockout_duration
    
    def reset_failed_attempts(self, user_id: str) -> None:
        """Reset failed attempts counter for a user."""
        if user_id in self.failed_attempts:
            del self.failed_attempts[user_id]
        if user_id in self.locked_out:
            del self.locked_out[user_id]
    
    def _calculate_risk_score(self, user_data: Dict[str, Any]) -> float:
        """Calculate risk score based on various factors."""
        score = 0.0
        
        # IP-based risk
        if user_data.get("ip_address") in self.ip_blacklist:
            score += 0.3
        
        # Geolocation risk
        if user_data.get("country_code") not in ["US", "GB", "CA"]:
            score += 0.2
            
        # Device risk
        if "mobile" not in user_data.get("user_agent", "").lower():
            score += 0.1
            
        # Time-based risk
        current_hour = datetime.utcnow().hour
        if current_hour < 6 or current_hour > 22:  # Night hours
            score += 0.1
            
        return min(score, 1.0)
    
    def get_risk_metrics(self) -> Dict[str, Any]:
        """Get current risk assessment metrics."""
        metrics = {
            "locked_out_users": len(self.locked_out),
            "failed_attempts": sum(self.failed_attempts.values()),
            "active_users": len(self.last_access),
            "risk_thresholds": self.risk_thresholds,
            "max_failed_attempts": self.max_failed_attempts
        }
        return metrics
