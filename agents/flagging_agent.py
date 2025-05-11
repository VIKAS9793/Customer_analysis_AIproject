"""
Human-in-the-Loop Flagging System

This module implements the flagging system for suspicious activities.
"""

import logging
from typing import Dict, Any, List
import json

class FlaggingError(Exception):
    """Raised when flagging fails"""
    pass

class FlaggingAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.flag_patterns = {
            "anomaly": {
                "description": "Transaction amount significantly higher than usual",
                "threshold": config.get("anomaly_threshold", 3.0)
            },
            "location": {
                "description": "Transaction from unusual location",
                "threshold": config.get("location_threshold", 1000)  # km
            },
            "velocity": {
                "description": "Multiple transactions in short time",
                "threshold": config.get("velocity_threshold", 5)  # transactions
            },
            "device": {
                "description": "Transaction from new device",
                "threshold": config.get("device_threshold", 1.0)
            }
        }
    
    def _generate_explanation(self, flag_type: str, details: Dict[str, Any]) -> str:
        """Generate human-readable explanation for flag"""
        pattern = self.flag_patterns[flag_type]
        return f"Transaction flagged as {flag_type}: {pattern['description']}\nDetails: {json.dumps(details)}"
    
    def flag_transaction(self, transaction: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Flag transaction if suspicious patterns are detected"""
        flags = []
        
        # Check for anomaly
        if "amount" in transaction:
            if transaction["amount"] > self.flag_patterns["anomaly"]["threshold"]:
                flags.append({
                    "type": "anomaly",
                    "explanation": self._generate_explanation(
                        "anomaly",
                        {"amount": transaction["amount"]}
                    )
                })
        
        # Check for location
        if "location" in transaction:
            if transaction["location_distance"] > self.flag_patterns["location"]["threshold"]:
                flags.append({
                    "type": "location",
                    "explanation": self._generate_explanation(
                        "location",
                        {"distance": transaction["location_distance"]}
                    )
                })
        
        # Check for velocity
        if "transaction_count" in transaction:
            if transaction["transaction_count"] > self.flag_patterns["velocity"]["threshold"]:
                flags.append({
                    "type": "velocity",
                    "explanation": self._generate_explanation(
                        "velocity",
                        {"count": transaction["transaction_count"]}
                    )
                })
        
        # Check for device
        if "new_device" in transaction:
            if transaction["new_device"]:
                flags.append({
                    "type": "device",
                    "explanation": self._generate_explanation(
                        "device",
                        {"device_id": transaction["device_id"]}
                    )
                })
        
        return flags
    
    def get_flag_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Get available flag patterns"""
        return self.flag_patterns
    
    def validate_flags(self, flags: List[Dict[str, Any]]) -> bool:
        """Validate flags against known patterns"""
        for flag in flags:
            if flag["type"] not in self.flag_patterns:
                self.logger.warning(f"Unknown flag type: {flag['type']}")
                return False
        return True
