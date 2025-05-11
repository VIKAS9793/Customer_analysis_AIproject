"""
Validators - Provides validation utilities for FinConnectAI system
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class Validator:
    """Base validator class."""
    
    def validate(self, data: Any) -> bool:
        """Validate the provided data.
        
        Args:
            data: Data to validate
            
        Returns:
            bool: True if data is valid
        """
        raise NotImplementedError("Subclasses must implement validate method")

class DecisionValidator(Validator):
    """Validates decision data."""
    
    def validate(self, decision: Dict[str, Any]) -> bool:
        """Validate decision data.
        
        Args:
            decision: Decision data to validate
            
        Returns:
            bool: True if decision is valid
        """
        try:
            # Required fields
            required_fields = ['decision', 'confidence', 'explanation', 'timestamp']
            if not all(field in decision for field in required_fields):
                return False
                
            # Decision must be valid value
            valid_decisions = ['APPROVE', 'REJECT', 'FLAG', 'ERROR']
            if decision.get('decision') not in valid_decisions:
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error validating decision: {str(e)}")
            return False

def create_validator(validator_type: str) -> Validator:
    """Create a validator instance based on type.
    
    Args:
        validator_type: Type of validator to create
        
    Returns:
        Validator instance
    """
    validators = {
        'decision': DecisionValidator
    }
    
    validator_class = validators.get(validator_type.lower())
    if validator_class:
        return validator_class()
    
    logger.warning(f"Unknown validator type: {validator_type}")
    return Validator()
