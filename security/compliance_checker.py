"""
Compliance Checker System

This module implements compliance checks for GDPR, DPDP Act (India), and other regulations.
"""

import logging
from typing import Dict, Any, List
import hashlib
from datetime import datetime
import logging

class ComplianceError(Exception):
    """Raised when compliance checks fail"""
    pass

class ComplianceChecker:
    def __init__(self, config: Dict[str, Any]):
        """Initialize compliance checker with configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.checks = {
            "GDPR": self._check_gdpr,
            "DPDP": self._check_dpdp,
            "DataRetention": self._check_data_retention,
            "Encryption": self._check_encryption
        }
        
    def _check_gdpr(self, data: Dict[str, Any]) -> Dict[str, bool]:
        """Check GDPR compliance"""
        results = {
            "purpose_limitation": True,
            "data_minimization": True,
            "storage_limitation": True,
            "data_protection": True
        }
        
        # Check data minimization (GDPR Art. 5(1)(c))
        if len(data) > self.config.get("max_data_fields", 10):
            results["data_minimization"] = False
            self.logger.warning("GDPR violation: Excessive data collection")
        
        # Check storage limitation (GDPR Art. 5(1)(e))
        if "timestamp" in data:
            age = datetime.now() - datetime.fromisoformat(data["timestamp"])
            max_age = self.config.get("data_retention_days", 90)
            if age.days > max_age:
                results["storage_limitation"] = False
                self.logger.warning(f"GDPR violation: Data retained for {age.days} days > {max_age} days")
        
        # Check data protection (GDPR Art. 5(1)(f))
        if "encryption_key" not in data:
            results["data_protection"] = False
            self.logger.warning("GDPR violation: Missing encryption")
        
        return results
    
    def _check_dpdp(self, data: Dict[str, Any]) -> Dict[str, bool]:
        """Check DPDP Act compliance"""
        results = {
            "data_localization": True,
            "consent_management": True,
            "data_security": True,
            "audit_trail": True
        }
        
        # Check data localization (DPDP Sec. 26)
        if "location" in data and data["location"] != "India":
            results["data_localization"] = False
            self.logger.warning("DPDP violation: Data not localized")
        
        # Check consent management (DPDP Sec. 11)
        if "consent" not in data:
            results["consent_management"] = False
            self.logger.warning("DPDP violation: Missing consent")
        
        return results
    
    def _check_encryption(self, data: Dict[str, Any]) -> Dict[str, bool]:
        """Check encryption compliance"""
        results = {
            "encryption_strength": True,
            "key_management": True,
            "data_integrity": True
        }
        
        # Check encryption strength (AES-256)
        if "encryption_key" in data:
            key_hash = hashlib.sha256(data["encryption_key"]).hexdigest()
            if len(key_hash) < 32:  # AES-256 requires 32-byte key
                results["encryption_strength"] = False
                self.logger.warning("Encryption violation: Weak key")
        
        # Check key management
        if "key_rotation" not in data:
            results["key_management"] = False
            self.logger.warning("Encryption violation: Missing key rotation")
        
        return results
    
    def check_compliance(self, data: Dict[str, Any]) -> Dict[str, Dict[str, bool]]:
        """Run all compliance checks"""
        results = {}
        for check_name, check_func in self.checks.items():
            try:
                results[check_name] = check_func(data)
            except Exception as e:
                self.logger.error(f"Compliance check {check_name} failed: {str(e)}")
                results[check_name] = {"error": True}
        
        return results
    
    def validate_compliance(self, data: Dict[str, Any]) -> bool:
        """Validate all compliance requirements"""
        results = self.check_compliance(data)
        
        # Check for any failures
        for check_name, check_results in results.items():
            for requirement, status in check_results.items():
                if not status:
                    error_msg = f"Compliance check failed: {check_name} - {requirement}"
                    self.logger.error(error_msg)
                    raise ComplianceError(error_msg)
        
        return True
