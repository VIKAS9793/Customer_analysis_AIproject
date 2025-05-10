"""
Explanation Agent

This module provides human-readable explanations for fraud detection decisions.
"""

import logging
from typing import Dict, Any, List
import json

class ExplanationAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.explanation_templates = {
            "anomaly": "Transaction amount of {amount} is {deviation}% higher than typical {category} transactions.",
            "location": "Transaction location {location} is {distance}km away from customer's usual activity region.",
            "time": "Transaction at {time} is outside customer's usual transaction hours ({usual_hours}).",
            "pattern": "Transaction pattern matches known fraud pattern: {pattern_description}.",
            "velocity": "Multiple transactions totaling {total_amount} detected within {time_window} minutes.",
            "device": "Transaction from new device {device_type} with different browser {browser}.",
            "merchant": "High-risk merchant category {merchant_category} with known fraud history."
        }
    
    def _format_amount(self, amount: float) -> str:
        """Format amount with appropriate currency symbol"""
        return f"₹{amount:,.2f}"
    
    def _format_time(self, timestamp: str) -> str:
        """Format time in readable format"""
        return datetime.fromisoformat(timestamp).strftime("%I:%M %p")
    
    def _generate_explanation(self, flag_type: str, details: Dict[str, Any]) -> str:
        """Generate explanation for a specific flag type"""
        template = self.explanation_templates.get(flag_type)
        if not template:
            return "Transaction flagged for potential fraud."
            
        if flag_type == "anomaly":
            return template.format(
                amount=self._format_amount(details["amount"]),
                deviation=details["deviation"]
            )
        elif flag_type == "location":
            return template.format(
                location=details["location"],
                distance=details["distance"]
            )
        elif flag_type == "time":
            return template.format(
                time=self._format_time(details["time"]),
                usual_hours=details["usual_hours"]
            )
        elif flag_type == "pattern":
            return template.format(
                pattern_description=details["description"]
            )
        elif flag_type == "velocity":
            return template.format(
                total_amount=self._format_amount(details["total_amount"]),
                time_window=details["time_window"]
            )
        elif flag_type == "device":
            return template.format(
                device_type=details["device_type"],
                browser=details["browser"]
            )
        elif flag_type == "merchant":
            return template.format(
                merchant_category=details["category"]
            )
            
        return "Transaction flagged for potential fraud."
    
    def generate_explanation(self, flags: List[Dict[str, Any]]) -> str:
        """Generate comprehensive explanation for multiple flags"""
        explanations = []
        for flag in flags:
            explanation = self._generate_explanation(flag["type"], flag["details"])
            explanations.append(explanation)
        
        return "\n\n".join(explanations)
    
    def validate_explanation(self, explanation: str) -> bool:
        """Validate that explanation contains required information"""
        required_elements = [
            "Transaction amount",
            "Location",
            "Time",
            "Pattern",
            "Velocity",
            "Device",
            "Merchant"
        ]
        
        for element in required_elements:
            if element.lower() in explanation.lower():
                return True
        
        self.logger.warning("Explanation missing required elements")
        return False
