"""
Fraud Detection Agent - Detects suspicious patterns in customer interactions
"""

import random
import logging
from typing import Dict, Any
from datetime import datetime
from app.models import Currency

logger = logging.getLogger(__name__)

class FraudAgent:
    def __init__(self):
        """Initialize the fraud detection agent with currency thresholds."""
        # Risk thresholds in USD
        self.HIGH_AMOUNT_THRESHOLD = {
            Currency.USD: 10000,
            Currency.EUR: 9000,
            Currency.GBP: 8000,
            Currency.JPY: 1100000,
            Currency.INR: 800000,
            Currency.CNY: 70000,
            Currency.AUD: 15000,
            Currency.CAD: 13000
        }
        self.MEDIUM_AMOUNT_THRESHOLD = {
            Currency.USD: 1000,
            Currency.EUR: 900,
            Currency.GBP: 800,
            Currency.JPY: 110000,
            Currency.INR: 80000,
            Currency.CNY: 7000,
            Currency.AUD: 1500,
            Currency.CAD: 1300
        }

    def analyze_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a transaction for potential fraud."""
        try:
            amount = transaction.get("amount", 0)
            currency = Currency(transaction.get("currency", Currency.USD.value))
            location = transaction.get("location")

            # Convert amount to USD for risk calculation
            usd_amount = self._convert_to_usd(amount, currency)
            risk_score = self._calculate_risk_score(usd_amount, location)

            # Decision logic
            if risk_score > 0.8:
                decision = "REJECT"
                confidence = 0.95
                action = "Block transaction and flag for review"
            elif risk_score > 0.6:
                decision = "REVIEW"
                confidence = 0.75
                action = "Hold for manual review"
            else:
                decision = "APPROVE"
                confidence = 0.85
                action = "Auto approve"

            explanation = self._generate_explanation(risk_score, usd_amount, currency, location)

            response = {
                "decision": decision,
                "confidence": confidence,
                "explanation": explanation,
                "risk_score": risk_score,
                "recommended_action": action,
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Fraud analysis completed for transaction: {transaction['transaction_id']}")
            return response

        except Exception as e:
            logger.error(f"Error in fraud analysis: {str(e)}")
            raise

    def _convert_to_usd(self, amount: float, currency: Currency) -> float:
        """Convert amount to USD using mock exchange rates."""
        rates = {
            Currency.USD: 1.0,
            Currency.EUR: 1.1,
            Currency.GBP: 1.25,
            Currency.JPY: 0.009,
            Currency.INR: 0.012,
            Currency.CNY: 0.14,
            Currency.AUD: 0.65,
            Currency.CAD: 0.74
        }
        return amount * rates[currency]

    def _calculate_risk_score(self, usd_amount: float, location: str = None) -> float:
        """Calculate risk score based on amount and location."""
        # Base risk from amount
        if usd_amount > self.HIGH_AMOUNT_THRESHOLD[Currency.USD]:
            base_risk = 0.7
        elif usd_amount > self.MEDIUM_AMOUNT_THRESHOLD[Currency.USD]:
            base_risk = 0.4
        else:
            base_risk = 0.2

        # Location-based risk adjustment
        location_risk = 0.0
        if not location:
            location_risk = 0.1  # Slight increase for unknown location
        else:
            # Example high-risk locations (for demonstration)
            high_risk_locations = ["anonymous proxy", "unknown"]
            if any(loc.lower() in location.lower() for loc in high_risk_locations):
                location_risk = 0.2

        # Combine risks with some randomness
        risk = base_risk + location_risk + random.uniform(-0.1, 0.1)
        return max(0.0, min(1.0, risk))  # Clamp between 0 and 1

    def _generate_explanation(self, risk_score: float, usd_amount: float, currency: Currency, location: str) -> str:
        """Generate explanation for the decision."""
        explanation = f"Risk score: {risk_score:.2f}\n"
        explanation += f"Amount: ${usd_amount:,.2f} {currency.value}\n"
        explanation += f"Location: {location}\n"

        # Amount-based explanation
        if usd_amount > self.HIGH_AMOUNT_THRESHOLD[Currency.USD]:
            explanation += "High transaction amount detected\n"
        elif usd_amount > self.MEDIUM_AMOUNT_THRESHOLD[Currency.USD]:
            explanation += "Medium transaction amount\n"

        # Location-based explanation
        if not location:
            explanation += "Unknown location increases risk\n"
        elif any(loc.lower() in location.lower() for loc in ["anonymous proxy", "unknown"]):
            explanation += "High-risk location detected\n"

        return explanation

    def _recommend_action(self, decision: str) -> str:
        """Recommend appropriate action based on decision."""
        if decision == "REJECT":
            return "Block transaction and flag for review"
        elif decision == "REVIEW":
            return "Hold for manual review"
        else:
            return "Auto approve"

    def _generate_error_response(self) -> Dict[str, Any]:
        """Generate error response."""
        return {
            "decision": "ERROR",
            "confidence": 0.0,
            "explanation": "Error occurred during fraud analysis",
            "recommended_action": "Manual review required",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _check_transaction_amount(self, transaction: Dict[str, Any]) -> float:
        """Check if transaction amount is suspicious."""
        amount = transaction.get("amount", 0)
        if amount > self.transaction_threshold:
            return 0.9  # High risk
        return 0.1  # Low risk

    def _check_transaction_frequency(self, transaction: Dict[str, Any]) -> float:
        """Check transaction frequency patterns."""
        # Implementation based on historical data
        return 0.5  # Placeholder

    def _check_location_risk(self, transaction: Dict[str, Any]) -> float:
        """Check risk associated with transaction location."""
        # Implementation based on location data
        return 0.3  # Placeholder
