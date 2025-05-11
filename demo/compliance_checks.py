"""
Compliance Checks Module for FinConnectAI

This module implements sophisticated compliance checks for financial customer data
based on real-world regulatory frameworks including GDPR, DPDP Act, SOX, and industry standards.
"""

import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
import re
import hashlib
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComplianceFramework:
    """Base class for compliance frameworks"""
    
    def __init__(self, name: str, version: str, description: str):
        self.name = name
        self.version = version
        self.description = description
        self.requirements = []
        
    def add_requirement(self, requirement_id: str, description: str, severity: str = "high"):
        """Add a compliance requirement"""
        self.requirements.append({
            "id": requirement_id,
            "description": description,
            "severity": severity
        })
        
    def get_requirements(self) -> List[Dict[str, str]]:
        """Get all requirements for this framework"""
        return self.requirements

class GDPRFramework(ComplianceFramework):
    """GDPR Compliance Framework"""
    
    def __init__(self):
        super().__init__(
            name="GDPR", 
            version="2016/679", 
            description="General Data Protection Regulation (EU)"
        )
        
        # Add GDPR requirements
        self.add_requirement("GDPR-A5-1-A", "Lawfulness, fairness and transparency", "critical")
        self.add_requirement("GDPR-A5-1-B", "Purpose limitation", "high")
        self.add_requirement("GDPR-A5-1-C", "Data minimization", "high")
        self.add_requirement("GDPR-A5-1-D", "Accuracy", "medium")
        self.add_requirement("GDPR-A5-1-E", "Storage limitation", "high")
        self.add_requirement("GDPR-A5-1-F", "Integrity and confidentiality", "critical")
        self.add_requirement("GDPR-A25", "Data protection by design and default", "high")
        self.add_requirement("GDPR-A30", "Records of processing activities", "medium")
        self.add_requirement("GDPR-A32", "Security of processing", "critical")
        self.add_requirement("GDPR-A33", "Notification of data breach", "high")
        
    def check_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check GDPR compliance for the provided data"""
        results = {}
        
        # Check lawfulness and consent
        results["GDPR-A5-1-A"] = {
            "compliant": data.get("consent", False),
            "details": "Explicit consent is " + ("present" if data.get("consent", False) else "missing")
        }
        
        # Check purpose limitation
        results["GDPR-A5-1-B"] = {
            "compliant": "purpose" in data and len(data.get("purpose", "")) > 0,
            "details": "Purpose statement is " + ("defined" if "purpose" in data and len(data.get("purpose", "")) > 0 else "missing")
        }
        
        # Check data minimization
        field_count = len(data)
        results["GDPR-A5-1-C"] = {
            "compliant": field_count <= 15,  # Example threshold
            "details": f"Data contains {field_count} fields, threshold is 15"
        }
        
        # Check storage limitation
        retention_days = data.get("data_retention_days", 0)
        results["GDPR-A5-1-E"] = {
            "compliant": retention_days <= 730,  # 2 years
            "details": f"Retention period is {retention_days} days, max allowed is 730 days"
        }
        
        # Check security of processing
        results["GDPR-A32"] = {
            "compliant": data.get("encryption_key") is not None,
            "details": "Encryption is " + ("enabled" if data.get("encryption_key") is not None else "disabled")
        }
        
        return results

class DPDPFramework(ComplianceFramework):
    """DPDP Act (India) Compliance Framework"""
    
    def __init__(self):
        super().__init__(
            name="DPDP Act", 
            version="2023", 
            description="Digital Personal Data Protection Act (India)"
        )
        
        # Add DPDP requirements
        self.add_requirement("DPDP-S7", "Notice and consent", "critical")
        self.add_requirement("DPDP-S8", "Quality of personal data", "medium")
        self.add_requirement("DPDP-S9", "Purpose limitation", "high")
        self.add_requirement("DPDP-S11", "Data retention", "high")
        self.add_requirement("DPDP-S19", "Security safeguards", "critical")
        self.add_requirement("DPDP-S20", "Data breach notification", "high")
        self.add_requirement("DPDP-S22", "Cross-border data transfers", "high")
        self.add_requirement("DPDP-S26", "Data localization", "high")
        
    def check_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check DPDP compliance for the provided data"""
        results = {}
        
        # Check notice and consent
        results["DPDP-S7"] = {
            "compliant": data.get("consent", False),
            "details": "Explicit consent is " + ("present" if data.get("consent", False) else "missing")
        }
        
        # Check purpose limitation
        results["DPDP-S9"] = {
            "compliant": "purpose" in data and len(data.get("purpose", "")) > 0,
            "details": "Purpose statement is " + ("defined" if "purpose" in data and len(data.get("purpose", "")) > 0 else "missing")
        }
        
        # Check data retention
        retention_days = data.get("data_retention_days", 0)
        results["DPDP-S11"] = {
            "compliant": retention_days <= 365,  # 1 year
            "details": f"Retention period is {retention_days} days, max allowed is 365 days"
        }
        
        # Check security safeguards
        results["DPDP-S19"] = {
            "compliant": data.get("encryption_key") is not None,
            "details": "Encryption is " + ("enabled" if data.get("encryption_key") is not None else "disabled")
        }
        
        # Check data localization
        is_india_data = data.get("location") == "India"
        results["DPDP-S26"] = {
            "compliant": is_india_data,
            "details": "Data is " + ("localized in India" if is_india_data else "not localized in India")
        }
        
        return results

class SOXFramework(ComplianceFramework):
    """Sarbanes-Oxley Act Compliance Framework"""
    
    def __init__(self):
        super().__init__(
            name="SOX", 
            version="2002", 
            description="Sarbanes-Oxley Act (US)"
        )
        
        # Add SOX requirements
        self.add_requirement("SOX-302", "Corporate responsibility for financial reports", "critical")
        self.add_requirement("SOX-404", "Management assessment of internal controls", "critical")
        self.add_requirement("SOX-409", "Real-time issuer disclosures", "high")
        self.add_requirement("SOX-802", "Criminal penalties for altering documents", "critical")
        self.add_requirement("SOX-806", "Protection for employees of publicly traded companies", "medium")
        
    def check_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check SOX compliance for the provided data"""
        results = {}
        
        # Check audit trail
        has_audit_trail = data.get("audit_trail", False)
        results["SOX-802"] = {
            "compliant": has_audit_trail,
            "details": "Audit trail is " + ("present" if has_audit_trail else "missing")
        }
        
        # Check internal controls
        has_internal_controls = data.get("internal_controls", False)
        results["SOX-404"] = {
            "compliant": has_internal_controls,
            "details": "Internal controls are " + ("documented" if has_internal_controls else "not documented")
        }
        
        # Check real-time disclosure capability
        has_realtime_reporting = data.get("realtime_reporting", False)
        results["SOX-409"] = {
            "compliant": has_realtime_reporting,
            "details": "Real-time reporting is " + ("enabled" if has_realtime_reporting else "not enabled")
        }
        
        return results

class PCI_DSS_Framework(ComplianceFramework):
    """PCI DSS Compliance Framework"""
    
    def __init__(self):
        super().__init__(
            name="PCI DSS", 
            version="4.0", 
            description="Payment Card Industry Data Security Standard"
        )
        
        # Add PCI DSS requirements
        self.add_requirement("PCI-R1", "Install and maintain network security controls", "critical")
        self.add_requirement("PCI-R2", "Apply secure configurations", "high")
        self.add_requirement("PCI-R3", "Protect stored account data", "critical")
        self.add_requirement("PCI-R4", "Protect cardholder data with strong cryptography", "critical")
        self.add_requirement("PCI-R7", "Restrict access to system components", "high")
        self.add_requirement("PCI-R8", "Identify users and authenticate access", "high")
        self.add_requirement("PCI-R10", "Log and monitor all access", "high")
        self.add_requirement("PCI-R12", "Support information security with policies", "medium")
        
    def check_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check PCI DSS compliance for the provided data"""
        results = {}
        
        # Check encryption for cardholder data
        has_encryption = data.get("encryption_key") is not None
        results["PCI-R4"] = {
            "compliant": has_encryption,
            "details": "Strong cryptography is " + ("used" if has_encryption else "not used")
        }
        
        # Check key rotation
        has_key_rotation = data.get("key_rotation", False)
        results["PCI-R4"] = {
            "compliant": has_key_rotation,
            "details": "Encryption key rotation is " + ("implemented" if has_key_rotation else "not implemented")
        }
        
        # Check logging
        has_logging = data.get("logging_enabled", False)
        results["PCI-R10"] = {
            "compliant": has_logging,
            "details": "Access logging is " + ("enabled" if has_logging else "disabled")
        }
        
        # Check for PCI data
        has_pci_data = data.get("contains_pci_data", False)
        if has_pci_data:
            # Additional checks for PCI data
            pci_data_masked = data.get("pci_data_masked", False)
            results["PCI-R3"] = {
                "compliant": pci_data_masked,
                "details": "PCI data is " + ("masked" if pci_data_masked else "not masked")
            }
        
        return results

class ComplianceChecker:
    """Main compliance checker that integrates multiple frameworks"""
    
    def __init__(self):
        self.frameworks = {
            "GDPR": GDPRFramework(),
            "DPDP": DPDPFramework(),
            "SOX": SOXFramework(),
            "PCI_DSS": PCI_DSS_Framework()
        }
        
    def get_framework(self, framework_name: str) -> ComplianceFramework:
        """Get a specific compliance framework"""
        return self.frameworks.get(framework_name)
    
    def get_all_frameworks(self) -> Dict[str, ComplianceFramework]:
        """Get all available compliance frameworks"""
        return self.frameworks
    
    def check_compliance(self, data: Dict[str, Any], frameworks: List[str] = None) -> Dict[str, Any]:
        """
        Check compliance against specified frameworks
        
        Args:
            data: The data to check for compliance
            frameworks: List of framework names to check against, or None for all frameworks
            
        Returns:
            Dict containing compliance results for each framework
        """
        if frameworks is None:
            frameworks = list(self.frameworks.keys())
            
        results = {}
        for framework_name in frameworks:
            if framework_name in self.frameworks:
                framework = self.frameworks[framework_name]
                framework_results = framework.check_compliance(data)
                results[framework_name] = framework_results
            else:
                logger.warning(f"Framework {framework_name} not found")
                
        # Calculate overall compliance score
        all_checks = []
        for framework_name, framework_results in results.items():
            for requirement, result in framework_results.items():
                all_checks.append(1.0 if result["compliant"] else 0.0)
        
        compliance_score = sum(all_checks) / len(all_checks) if all_checks else 0.0
        
        # Determine overall compliance status
        if compliance_score >= 0.9:
            compliance_status = "COMPLIANT"
        elif compliance_score >= 0.7:
            compliance_status = "PARTIALLY COMPLIANT"
        else:
            compliance_status = "NON-COMPLIANT"
            
        return {
            "framework_results": results,
            "compliance_score": compliance_score,
            "compliance_status": compliance_status,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_compliance_report(self, compliance_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a detailed compliance report from compliance check results
        
        Args:
            compliance_results: Results from check_compliance
            
        Returns:
            Dict containing a formatted compliance report
        """
        framework_results = compliance_results.get("framework_results", {})
        compliance_score = compliance_results.get("compliance_score", 0.0)
        compliance_status = compliance_results.get("compliance_status", "UNKNOWN")
        
        # Count compliant and non-compliant checks
        total_checks = 0
        compliant_checks = 0
        critical_violations = 0
        high_violations = 0
        medium_violations = 0
        
        violations_by_framework = {}
        
        for framework_name, framework_results in framework_results.items():
            framework_violations = []
            
            for requirement_id, result in framework_results.items():
                total_checks += 1
                if result["compliant"]:
                    compliant_checks += 1
                else:
                    # Get requirement details
                    framework = self.frameworks.get(framework_name)
                    requirement = next((r for r in framework.get_requirements() if r["id"] == requirement_id), None)
                    
                    if requirement:
                        severity = requirement.get("severity", "medium")
                        if severity == "critical":
                            critical_violations += 1
                        elif severity == "high":
                            high_violations += 1
                        else:
                            medium_violations += 1
                            
                        framework_violations.append({
                            "requirement_id": requirement_id,
                            "description": requirement.get("description", "Unknown"),
                            "severity": severity,
                            "details": result.get("details", "")
                        })
            
            if framework_violations:
                violations_by_framework[framework_name] = framework_violations
        
        # Generate report
        report = {
            "summary": {
                "compliance_score": compliance_score,
                "compliance_status": compliance_status,
                "total_checks": total_checks,
                "compliant_checks": compliant_checks,
                "non_compliant_checks": total_checks - compliant_checks,
                "critical_violations": critical_violations,
                "high_violations": high_violations,
                "medium_violations": medium_violations
            },
            "violations_by_framework": violations_by_framework,
            "timestamp": datetime.now().isoformat(),
            "report_id": f"COMP-{datetime.now().strftime('%Y%m%d%H%M%S')}-{hashlib.md5(str(compliance_results).encode()).hexdigest()[:8]}"
        }
        
        return report

def validate_customer_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate customer data for common issues
    
    Args:
        data: Customer data to validate
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Check required fields
    required_fields = ["customer_id", "timestamp"]
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    # Validate customer ID format (example: alphanumeric with optional hyphens)
    if "customer_id" in data:
        customer_id = data["customer_id"]
        if not re.match(r'^[A-Za-z0-9\-]+$', customer_id):
            errors.append(f"Invalid customer ID format: {customer_id}")
    
    # Validate timestamp
    if "timestamp" in data:
        try:
            timestamp = datetime.fromisoformat(data["timestamp"])
            # Check if timestamp is in the future
            if timestamp > datetime.now() + timedelta(minutes=5):  # Allow 5 minutes for clock skew
                errors.append(f"Timestamp is in the future: {data['timestamp']}")
        except (ValueError, TypeError):
            errors.append(f"Invalid timestamp format: {data['timestamp']}")
    
    # Validate email if present
    if "email" in data and data["email"]:
        email = data["email"]
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append(f"Invalid email format: {email}")
    
    # Validate phone if present
    if "phone" in data and data["phone"]:
        phone = data["phone"]
        if not re.match(r'^\+?[0-9\-\s()]+$', phone):
            errors.append(f"Invalid phone format: {phone}")
    
    return len(errors) == 0, errors

def check_pii_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check for PII data in the provided data
    
    Args:
        data: Data to check for PII
        
    Returns:
        Dict containing PII detection results
    """
    pii_types = {
        "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        "phone": r'(\+\d{1,3}[\s-])?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}',
        "ssn": r'\d{3}-\d{2}-\d{4}',
        "credit_card": r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}',
        "ip_address": r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
        "date_of_birth": r'\d{2}[/-]\d{2}[/-]\d{4}'
    }
    
    pii_found = {}
    
    # Convert data to string for regex searching
    data_str = json.dumps(data)
    
    for pii_type, pattern in pii_types.items():
        matches = re.findall(pattern, data_str)
        if matches:
            pii_found[pii_type] = len(matches)
    
    return {
        "pii_detected": len(pii_found) > 0,
        "pii_types": pii_found,
        "requires_special_handling": any(pii_type in pii_found for pii_type in ["ssn", "credit_card"])
    }

# Example usage
if __name__ == "__main__":
    # Create a compliance checker
    checker = ComplianceChecker()
    
    # Example data
    data = {
        "customer_id": "CUST-12345",
        "timestamp": datetime.now().isoformat(),
        "location": "United States",
        "consent": True,
        "purpose": "Customer analysis for service improvement",
        "encryption_key": "sample_key",
        "key_rotation": True,
        "data_retention_days": 180,
        "logging_enabled": True,
        "audit_trail": True,
        "internal_controls": True,
        "realtime_reporting": False
    }
    
    # Check compliance
    compliance_results = checker.check_compliance(data, ["GDPR", "PCI_DSS"])
    
    # Generate report
    report = checker.generate_compliance_report(compliance_results)
    
    print(f"Compliance Score: {compliance_results['compliance_score']:.2f}")
    print(f"Compliance Status: {compliance_results['compliance_status']}")
    print(f"Total Checks: {report['summary']['total_checks']}")
    print(f"Compliant Checks: {report['summary']['compliant_checks']}")
    print(f"Non-Compliant Checks: {report['summary']['non_compliant_checks']}")
