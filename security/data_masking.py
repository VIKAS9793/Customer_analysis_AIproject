"""
Data Masking System

This module implements data masking for sensitive information.
"""

from typing import Dict, Any, Optional
import logging
import re
from cryptography.fernet import Fernet

class MaskingError(Exception):
    """Raised when masking fails"""
    pass

class DataMasker:
    def __init__(self, config: Dict[str, Any]):
        """Initialize data masker with configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.sensitive_fields = config.get("sensitive_fields", [])
        self.masking_type = config.get("masking_type", "partial")
        
        if self.masking_type not in ["partial", "full", "hash"]:
            raise MaskingError("Invalid masking type. Must be 'partial', 'full', or 'hash'")
    
    def mask_credit_card(self, card_number: str) -> str:
        """Mask credit card number"""
        try:
            if self.masking_type == "partial":
                return f"****-****-****-{card_number[-4:]}"
            elif self.masking_type == "full":
                return "XXXXXXXXXXXXXXXX"
            elif self.masking_type == "hash":
                return self._hash_value(card_number)
        except Exception as e:
            self.logger.error(f"Credit card masking failed: {str(e)}")
            raise MaskingError(f"Failed to mask credit card: {str(e)}")
    
    def mask_ssn(self, ssn: str) -> str:
        """Mask SSN"""
        try:
            if self.masking_type == "partial":
                return f"***-**-{ssn[-4:]}"
            elif self.masking_type == "full":
                return "XXX-XX-XXXX"
            elif self.masking_type == "hash":
                return self._hash_value(ssn)
        except Exception as e:
            self.logger.error(f"SSN masking failed: {str(e)}")
            raise MaskingError(f"Failed to mask SSN: {str(e)}")
    
    def mask_phone(self, phone: str) -> str:
        """Mask phone number"""
        try:
            if self.masking_type == "partial":
                return f"***-***-{phone[-4:]}"
            elif self.masking_type == "full":
                return "XXX-XXX-XXXX"
            elif self.masking_type == "hash":
                return self._hash_value(phone)
        except Exception as e:
            self.logger.error(f"Phone masking failed: {str(e)}")
            raise MaskingError(f"Failed to mask phone: {str(e)}")
    
    def mask_email(self, email: str) -> str:
        """Mask email address"""
        try:
            if self.masking_type == "partial":
                parts = email.split('@')
                username = parts[0]
                domain = parts[1]
                return f"{username[0]}***@{domain}"
            elif self.masking_type == "full":
                return "user@domain.com"
            elif self.masking_type == "hash":
                return self._hash_value(email)
        except Exception as e:
            self.logger.error(f"Email masking failed: {str(e)}")
            raise MaskingError(f"Failed to mask email: {str(e)}")
    
    def mask_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive data in a dictionary"""
        try:
            masked_data = data.copy()
            for field in self.sensitive_fields:
                if field in masked_data:
                    value = masked_data[field]
                    
                    if isinstance(value, str):
                        if re.match(r"\d{16}", value):  # Credit card
                            masked_data[field] = self.mask_credit_card(value)
                        elif re.match(r"\d{9}", value):  # SSN
                            masked_data[field] = self.mask_ssn(value)
                        elif re.match(r"\d{10}", value):  # Phone
                            masked_data[field] = self.mask_phone(value)
                        elif re.match(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", value):
                            masked_data[field] = self.mask_email(value)
                        else:
                            if self.masking_type == "partial":
                                masked_data[field] = f"{value[0]}***{value[-1]}"
                            elif self.masking_type == "full":
                                masked_data[field] = "XXXXX"
                            elif self.masking_type == "hash":
                                masked_data[field] = self._hash_value(value)
            
            return masked_data
        except Exception as e:
            self.logger.error(f"Data masking failed: {str(e)}")
            raise MaskingError(f"Failed to mask data: {str(e)}")
    
    def _hash_value(self, value: str) -> str:
        """Hash a value using secure hashing"""
        try:
            # In real implementation, use HSM for hashing
            # For simulation, use Fernet
            key = Fernet.generate_key()
            fernet = Fernet(key)
            return fernet.encrypt(value.encode()).decode()
        except Exception as e:
            self.logger.error(f"Hashing failed: {str(e)}")
            raise MaskingError(f"Failed to hash value: {str(e)}")
