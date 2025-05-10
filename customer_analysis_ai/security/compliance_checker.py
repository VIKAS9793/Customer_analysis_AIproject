from typing import Dict, Any, List
from datetime import datetime, timedelta

class ComplianceError(Exception):
    """Raised when compliance validation fails."""
    pass

class ComplianceChecker:
    def __init__(self, config: Dict[str, Any]):
        """Initialize the compliance checker."""
        self.config = config or {}
        self.audit_log = []
        
        # Define compliance rules
        self.compliance_rules = {
            'data_minimization': {
                'check': self._check_data_minimization,
                'max_fields': config.get('max_data_fields', 10)
            },
            'data_retention': {
                'check': self._check_data_retention,
                'max_days': config.get('data_retention_days', 90)
            },
            'data_protection': {
                'check': self._check_data_protection,
                'required_fields': ['encryption_key']
            },
            'data_localization': {
                'check': self._check_data_localization,
                'allowed_locations': ['India']
            },
            'consent_management': {
                'check': self._check_consent,
                'required': True
            },
            'encryption': {
                'check': self._check_encryption,
                'min_key_length': 32,
                'rotation_days': config.get('encryption_key_rotation_days', 90)
            }
        }

    def validate_compliance(self, data: Dict[str, Any]) -> bool:
        """Validate compliance and raise ComplianceError if any rule fails."""
        for rule_name, rule_config in self.compliance_rules.items():
            check_func = rule_config['check']
            if not check_func(data, rule_config):
                raise ComplianceError(f'Compliance validation failed: {rule_name}')
        return True

    def check_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance and return detailed results without raising errors."""
        timestamp = datetime.now().isoformat()
        results = {}
        
        # Check each compliance rule
        for rule_name, rule_config in self.compliance_rules.items():
            check_func = rule_config['check']
            passed = check_func(data, rule_config)
            results[rule_name] = {
                'passed': passed,
                'timestamp': timestamp
            }
        
        # Log the compliance check
        self.audit_log.append({
            'timestamp': timestamp,
            'data_id': data.get('id', 'unknown'),
            'results': results
        })
        
        return results

    def _check_data_minimization(self, data: Dict[str, Any], rule_config: Dict[str, Any]) -> bool:
        """Check if data has more fields than allowed."""
        return len(data) <= rule_config['max_fields']
    
    def _check_data_retention(self, data: Dict[str, Any], rule_config: Dict[str, Any]) -> bool:
        """Check if data is within retention period."""
        if 'timestamp' not in data:
            return False
        try:
            timestamp = datetime.fromisoformat(data['timestamp'])
            age = (datetime.utcnow() - timestamp).days
            return age <= rule_config['max_days']
        except (ValueError, TypeError):
            return False
    
    def _check_data_protection(self, data: Dict[str, Any], rule_config: Dict[str, Any]) -> bool:
        """Check if required protection fields are present."""
        return all(field in data for field in rule_config['required_fields'])
    
    def _check_data_localization(self, data: Dict[str, Any], rule_config: Dict[str, Any]) -> bool:
        """Check if data location is allowed."""
        return data.get('location') in rule_config['allowed_locations']
    
    def _check_consent(self, data: Dict[str, Any], rule_config: Dict[str, Any]) -> bool:
        """Check if consent is given."""
        return data.get('consent', False) is True
    
    def _check_encryption(self, data: Dict[str, Any], rule_config: Dict[str, Any]) -> bool:
        """Check encryption requirements."""
        if 'encryption_key' not in data:
            return False
            
        key = data['encryption_key']
        if len(key) < rule_config['min_key_length']:
            return False
            
        # Check key rotation if timestamp is present
        if 'timestamp' in data:
            try:
                timestamp = datetime.fromisoformat(data['timestamp'])
                age = (datetime.utcnow() - timestamp).days
                if age > rule_config['rotation_days']:
                    return False
            except (ValueError, TypeError):
                return False
                
        return True

    def get_audit_log(self, start_time: datetime = None) -> List[Dict[str, Any]]:
        """Get the audit log, optionally filtered by start time."""
        if start_time is None:
            return self.audit_log
            
        return [
            entry for entry in self.audit_log 
            if datetime.fromisoformat(entry['timestamp']) >= start_time
        ]
