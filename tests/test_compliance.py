import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from security.compliance_checker import ComplianceChecker, ComplianceError
from security.risk_assessment import RiskAssessment
from security.audit_trail import AuditTrail

class TestComplianceChecker(unittest.TestCase):
    def setUp(self):
        self.config = {
            "data_protection": {
                "encryption_required": True,
                "key_rotation_days": 90,
                "backup_retention_days": 365
            },
            "data_retention": {
                "max_days": 365,
                "audit_logs": 365,
                "access_logs": 90
            },
            "audit": {
                "enabled": True,
                "log_level": "INFO",
                "retention_days": 365
            },
            "encryption": {
                "algorithm": "AES-256-GCM",
                "key_size": 256
            }
        }
        self.compliance_checker = ComplianceChecker(self.config)
        
    def test_data_protection_check(self):
        """Test data protection compliance check"""
        # Test with compliant data
        data = {
            "encryption": True,
            "key_rotation_age": 89,
            "backup_age": 364
        }
        result = self.compliance_checker.check_data_protection(data)
        self.assertTrue(result["compliant"])
        
        # Test with non-compliant data
        data = {
            "encryption": False,
            "key_rotation_age": 91,
            "backup_age": 366
        }
        result = self.compliance_checker.check_data_protection(data)
        self.assertFalse(result["compliant"])
        self.assertIn("Encryption required", result["issues"])
        self.assertIn("Key rotation overdue", result["issues"])
        self.assertIn("Backup retention exceeded", result["issues"])
        
    def test_data_retention_check(self):
        """Test data retention compliance check"""
        # Test with compliant retention
        data = {
            "creation_date": (datetime.now() - timedelta(days=364)).isoformat(),
            "type": "audit_log"
        }
        result = self.compliance_checker.check_data_retention(data)
        self.assertTrue(result["compliant"])
        
        # Test with expired retention
        data = {
            "creation_date": (datetime.now() - timedelta(days=366)).isoformat(),
            "type": "audit_log"
        }
        result = self.compliance_checker.check_data_retention(data)
        self.assertFalse(result["compliant"])
        self.assertIn("Retention period exceeded", result["issues"])
        
    def test_audit_trail_check(self):
        """Test audit trail compliance check"""
        # Test with compliant audit trail
        audit_data = {
            "event_type": "user_login",
            "timestamp": datetime.now().isoformat(),
            "user_id": "user123",
            "risk_level": "low"
        }
        result = self.compliance_checker.check_audit_trail(audit_data)
        self.assertTrue(result["compliant"])
        
        # Test with non-compliant audit trail
        audit_data = {
            "event_type": "user_login",
            "timestamp": datetime.now().isoformat(),
            "user_id": "user123"
        }
        result = self.compliance_checker.check_audit_trail(audit_data)
        self.assertFalse(result["compliant"])
        self.assertIn("Missing risk level", result["issues"])
        
    def test_encryption_check(self):
        """Test encryption compliance check"""
        # Test with compliant encryption
        encryption_data = {
            "algorithm": "AES-256-GCM",
            "key_size": 256,
            "key_rotation_age": 89
        }
        result = self.compliance_checker.check_encryption(encryption_data)
        self.assertTrue(result["compliant"])
        
        # Test with non-compliant encryption
        encryption_data = {
            "algorithm": "AES-128-CBC",
            "key_size": 128,
            "key_rotation_age": 91
        }
        result = self.compliance_checker.check_encryption(encryption_data)
        self.assertFalse(result["compliant"])
        self.assertIn("Weak encryption algorithm", result["issues"])
        self.assertIn("Key size too small", result["issues"])
        self.assertIn("Key rotation overdue", result["issues"])
        
    def test_compliance_validation(self):
        """Test overall compliance validation"""
        # Test with compliant data
        data = {
            "encryption": True,
            "key_rotation_age": 89,
            "backup_age": 364,
            "creation_date": (datetime.now() - timedelta(days=364)).isoformat(),
            "type": "audit_log",
            "algorithm": "AES-256-GCM",
            "key_size": 256
        }
        result = self.compliance_checker.validate_compliance(data)
        self.assertTrue(result["compliant"])
        
        # Test with non-compliant data
        data = {
            "encryption": False,
            "key_rotation_age": 91,
            "backup_age": 366,
            "creation_date": (datetime.now() - timedelta(days=366)).isoformat(),
            "type": "audit_log",
            "algorithm": "AES-128-CBC",
            "key_size": 128
        }
        result = self.compliance_checker.validate_compliance(data)
        self.assertFalse(result["compliant"])
        self.assertIn("Encryption required", result["issues"])
        self.assertIn("Key rotation overdue", result["issues"])
        self.assertIn("Backup retention exceeded", result["issues"])
        self.assertIn("Retention period exceeded", result["issues"])
        self.assertIn("Weak encryption algorithm", result["issues"])
        self.assertIn("Key size too small", result["issues"])
        
    def test_compliance_exception(self):
        """Test compliance exception handling"""
        with self.assertRaises(ComplianceError):
            self.compliance_checker.validate_compliance({})

if __name__ == '__main__':
    unittest.main()
