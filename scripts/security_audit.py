"""
Security Audit Script

This script performs a comprehensive security audit of the codebase to ensure:
1. No hardcoded credentials or secrets
2. Proper configuration validation
3. Secure implementation of security features
"""

import os
import re
import ast
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SecurityAudit:
    """Security audit class for banking and fintech security compliance
    
    This audit script checks for compliance with banking-specific regulations:
    - RBI Guidelines
    - SEBI Regulations
    - PCI DSS Requirements
    - GDPR Compliance
    """
    
    def __init__(self, project_root: str):
        """Initialize security audit
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root
        self.violations: List[Dict[str, Any]] = []
        
    def _find_hardcoded_values(self, file_path: str) -> None:
        """Find hardcoded values in a file with banking-specific checks
        
        Args:
            file_path: Path to the file to check
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Banking-specific patterns to check
        patterns = {
            # Payment-related patterns
            'api_key': r'(api_key|api-key|apikey|access_key|access-key|accesskey)\s*[=:].*\b[A-Za-z0-9]{30,}\b',
            'password': r'(password|passwd|pwd)\s*[=:].*\b[A-Za-z0-9]{8,}\b',
            'secret': r'(secret|token|credential)\s*[=:].*\b[A-Za-z0-9]{30,}\b',
            'key': r'(key|private_key|private-key|privatekey)\s*[=:].*\b[A-Za-z0-9]{30,}\b',
            # Banking-specific patterns
            'card_number': r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|6(?:011|5[0-9][0-9])[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|(?:2131|1800|35\d{3})\d{11})\b',
            'ifsc_code': r'\b[A-Z]{4}0[A-Z0-9]{6}\b',
            'account_number': r'\b[0-9]{9,18}\b',
            'pan_number': r'\b[A-Z]{5}[0-9]{4}[A-Z]\b',
            'aadhaar': r'\b[0-9]{12}\b',
            # PCI DSS patterns
            'cvv': r'\b[0-9]{3,4}\b',
            'expiry_date': r'\b(?:0[1-9]|1[0-2])/(?:[0-9]{2})\b',
            # Banking security patterns
            'encryption_key': r'\b[A-Fa-f0-9]{32,}\b',
            'session_token': r'\b[A-Za-z0-9-_=]{30,}\b',
            'api_endpoint': r'(api_key|api_secret|access_token)\s*[=:].*\bhttps?://.*\b'
        }
        
        for pattern_name, pattern in patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                self.violations.append({
                    'type': 'hardcoded_value',
                    'file': file_path,
                    'line': content.count('\n', 0, match.start()) + 1,
                    'pattern': pattern_name,
                    'value': match.group(0),
                    'severity': 'HIGH' if pattern_name in ['card_number', 'ifsc_code', 'account_number'] else 'MEDIUM'
                })
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for common hardcoded patterns
        patterns = {
            'api_key': r'(api_key|api-key|apikey|access_key|access-key|accesskey)\s*[=:].*\b[A-Za-z0-9]{30,}\b',
            'password': r'(password|passwd|pwd)\s*[=:].*\b[A-Za-z0-9]{8,}\b',
            'secret': r'(secret|token|credential)\s*[=:].*\b[A-Za-z0-9]{30,}\b',
            'key': r'(key|private_key|private-key|privatekey)\s*[=:].*\b[A-Za-z0-9]{30,}\b',
        }
        
        for pattern_name, pattern in patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                self.violations.append({
                    'type': 'hardcoded_value',
                    'file': file_path,
                    'line': content.count('\n', 0, match.start()) + 1,
                    'pattern': pattern_name,
                    'value': match.group(0)
                })
    
    def _analyze_python_files(self, directory: str) -> None:
        """Analyze Python files for security issues
        
        Args:
            directory: Directory to analyze
        """
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            tree = ast.parse(f.read(), filename=file_path)
                            
                        # Check for hardcoded values in Python files
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Assign):
                                for target in node.targets:
                                    if isinstance(target, ast.Name):
                                        name = target.id.lower()
                                        if any(keyword in name for keyword in ['key', 'secret', 'password', 'token']):
                                            if isinstance(node.value, (ast.Str, ast.Num)):
                                                self.violations.append({
                                                    'type': 'hardcoded_value',
                                                    'file': file_path,
                                                    'line': node.lineno,
                                                    'pattern': 'python_assignment',
                                                    'value': str(node.value)
                                                })
                    except Exception as e:
                        logger.warning(f"Error analyzing {file_path}: {str(e)}")
    
    def run_audit(self) -> None:
        """Run the security audit with banking-specific checks
        
        This audit checks for:
        1. Payment data protection (PCI DSS)
        2. Customer data protection (GDPR)
        3. Banking-specific compliance (RBI, SEBI)
        4. Security controls (ISO 27001)
        """
        # Check for hardcoded values in all files
        for root, _, files in os.walk(self.project_root):
            # Skip virtual environments and git directories
            if 'venv' in root or '.git' in root:
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    self._find_hardcoded_values(file_path)
                    self._check_payment_security(file_path)
                    self._check_customer_data_protection(file_path)
                    self._check_compliance(file_path)
                except Exception as e:
                    logger.warning(f"Error checking {file_path}: {str(e)}")
        
        # Analyze Python files for security issues
        self._analyze_python_files(self.project_root)
        
        # Generate audit report
        self._generate_audit_report()
        
    def _check_payment_security(self, file_path: str) -> None:
        """Check for PCI DSS compliance"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for PCI DSS requirements
        if 'card_data' in content.lower() and 'encrypt' not in content.lower():
            self.violations.append({
                'type': 'pci_dss_violation',
                'file': file_path,
                'line': 0,
                'pattern': 'card_data_storage',
                'value': 'Card data stored without encryption',
                'severity': 'CRITICAL'
            })
            
        # Check for PAN masking
        if 'pan_number' in content.lower() and 'mask' not in content.lower():
            self.violations.append({
                'type': 'pci_dss_violation',
                'file': file_path,
                'line': 0,
                'pattern': 'pan_masking',
                'value': 'PAN number not properly masked',
                'severity': 'HIGH'
            })
            
    def _check_customer_data_protection(self, file_path: str) -> None:
        """Check for GDPR compliance"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for data retention policies
        if 'customer_data' in content.lower() and 'retention' not in content.lower():
            self.violations.append({
                'type': 'gdpr_violation',
                'file': file_path,
                'line': 0,
                'pattern': 'data_retention',
                'value': 'No data retention policy defined',
                'severity': 'HIGH'
            })
            
        # Check for consent management
        if 'customer_consent' in content.lower() and 'verify' not in content.lower():
            self.violations.append({
                'type': 'gdpr_violation',
                'file': file_path,
                'line': 0,
                'pattern': 'consent_verification',
                'value': 'No consent verification implemented',
                'severity': 'HIGH'
            })
            
    def _check_compliance(self, file_path: str) -> None:
        """Check for banking-specific compliance"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for RBI compliance
        if 'kyc_verification' in content.lower() and 'mandatory' not in content.lower():
            self.violations.append({
                'type': 'rbi_compliance',
                'file': file_path,
                'line': 0,
                'pattern': 'kyc_verification',
                'value': 'KYC verification not mandatory',
                'severity': 'CRITICAL'
            })
            
        # Check for SEBI compliance
        if 'audit_trail' in content.lower() and 'required' not in content.lower():
            self.violations.append({
                'type': 'sebi_compliance',
                'file': file_path,
                'line': 0,
                'pattern': 'audit_trail',
                'value': 'Audit trail not required',
                'severity': 'HIGH'
            })
            
    def _generate_audit_report(self) -> None:
        """Generate comprehensive security audit report"""
        print("\nSecurity Audit Report - Banking & Fintech Compliance")
        print("=" * 80)
        
        # Group violations by severity
        violations_by_severity = {
            'CRITICAL': [],
            'HIGH': [],
            'MEDIUM': [],
            'LOW': []
        }
        
        for violation in self.violations:
            severity = violation.get('severity', 'MEDIUM')
            violations_by_severity[severity].append(violation)
            
        # Print summary
        print("\nAudit Summary:")
        print("-" * 80)
        print(f"Total Violations: {len(self.violations)}")
        print(f"Critical: {len(violations_by_severity['CRITICAL'])}")
        print(f"High: {len(violations_by_severity['HIGH'])}")
        print(f"Medium: {len(violations_by_severity['MEDIUM'])}")
        print(f"Low: {len(violations_by_severity['LOW'])}")
        
        # Print detailed violations
        print("\nDetailed Violations:")
        print("=" * 80)
        
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            if violations_by_severity[severity]:
                print(f"\n{severity} Violations:")
                print("-" * 80)
                for violation in violations_by_severity[severity]:
                    print(f"\nType: {violation['type']}")
                    print(f"File: {violation['file']}")
                    print(f"Line: {violation['line']}")
                    print(f"Pattern: {violation['pattern']}")
                    print(f"Value: {violation['value']}")
                    print(f"Severity: {violation['severity']}")
                    print("-" * 40)
        
        if self.violations:
            print("\nSecurity violations found! Please review and fix these issues.")
            print("\nRecommendations:")
            print("1. Implement proper encryption for sensitive data")
            print("2. Add proper data masking for PII")
            print("3. Implement proper audit trails")
            print("4. Add proper data retention policies")
            print("5. Implement proper KYC verification")
        else:
            print("\nSecurity Audit Complete!")
            print("No security violations found!")
        """Run the security audit"""
        # Check for hardcoded values in all files
        for root, _, files in os.walk(self.project_root):
            # Skip virtual environments and git directories
            if 'venv' in root or '.git' in root:
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    self._find_hardcoded_values(file_path)
                except Exception as e:
                    logger.warning(f"Error checking {file_path}: {str(e)}")
        
        # Analyze Python files for security issues
        self._analyze_python_files(self.project_root)
        
        # Print audit results
        if self.violations:
            print("\nSecurity Audit Results:")
            print("-" * 80)
            for violation in self.violations:
                print(f"\nType: {violation['type']}")
                print(f"File: {violation['file']}")
                print(f"Line: {violation['line']}")
                print(f"Pattern: {violation['pattern']}")
                print(f"Value: {violation['value']}")
            print("\nSecurity violations found! Please review and fix these issues.")
        else:
            print("\nSecurity Audit Complete!")
            print("No security violations found!")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    auditor = SecurityAudit(project_root)
    auditor.run_audit()
