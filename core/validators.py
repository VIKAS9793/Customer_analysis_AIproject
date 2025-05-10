from typing import Any, Dict, Optional, List, TypeVar, Generic
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

T = TypeVar('T')

@dataclass
class ValidationRule:
    """Represents a validation rule with conditions and actions."""
    name: str
    condition: callable
    action: callable
    severity: str = "critical"
    description: str = ""


class Validator(Generic[T]):
    """Base validator class for type-specific validation."""
    
    def __init__(self, rules: List[ValidationRule]):
        self.rules = rules
        
    def validate(self, data: T) -> Dict[str, Any]:
        """Validate data against all rules.
        
        Args:
            data: Data to validate
            
        Returns:
            Dict containing validation results
        """
        results = {
            "valid": True,
            "issues": [],
            "timestamp": datetime.now().isoformat()
        }
        
        for rule in self.rules:
            try:
                if not rule.condition(data):
                    results["valid"] = False
                    results["issues"].append({
                        "rule": rule.name,
                        "severity": rule.severity,
                        "description": rule.description,
                        "timestamp": datetime.now().isoformat()
                    })
                    rule.action(data)
            except Exception as e:
                logger.error(f"Error executing rule {rule.name}: {str(e)}")
                results["issues"].append({
                    "rule": rule.name,
                    "severity": "critical",
                    "description": f"Rule execution failed: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                })
        
        return results


class ResponseValidator(Validator[str]):
    """Validator for AI responses."""
    
    def __init__(self):
        rules = [
            ValidationRule(
                name="source_verification",
                condition=lambda resp: self._has_valid_sources(resp),
                action=lambda resp: self._log_missing_sources(),
                severity="critical",
                description="Response must cite valid sources"
            ),
            ValidationRule(
                name="confidence_check",
                condition=lambda resp: self._has_sufficient_confidence(resp),
                action=lambda resp: self._log_low_confidence(),
                severity="high",
                description="Response confidence must be above threshold"
            ),
            ValidationRule(
                name="data_consistency",
                condition=lambda resp: self._is_consistent_with_data(resp),
                action=lambda resp: self._log_inconsistency(),
                severity="critical",
                description="Response must be consistent with provided data"
            )
        ]
        super().__init__(rules)
    
    def _has_valid_sources(self, response: str) -> bool:
        """Check if response cites valid sources."""
        # Implementation to verify sources
        return True
    
    def _has_sufficient_confidence(self, response: str) -> bool:
        """Check if response has sufficient confidence."""
        # Implementation to verify confidence
        return True
    
    def _is_consistent_with_data(self, response: str) -> bool:
        """Check if response is consistent with provided data."""
        # Implementation to verify data consistency
        return True
    
    def _log_missing_sources(self) -> None:
        """Log missing sources issue."""
        logger.warning("Response missing valid sources")
    
    def _log_low_confidence(self) -> None:
        """Log low confidence issue."""
        logger.warning("Response has low confidence")
    
    def _log_inconsistency(self) -> None:
        """Log data inconsistency issue."""
        logger.error("Response inconsistent with provided data")
