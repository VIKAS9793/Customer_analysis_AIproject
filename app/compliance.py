"""Compliance utility for AI-powered fraud detection."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)

class Region(Enum):
    """Supported regulatory regions."""
    EU = "EU"
    INDIA = "INDIA"
    US = "US"
    UK = "UK"
    SINGAPORE = "SINGAPORE"

class RiskLevel(Enum):
    """Risk levels for AI models."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class ComplianceRequirement:
    """Represents a compliance requirement for a specific region."""
    region: Region
    regulations: List[str]
    risk_level: RiskLevel
    required_validations: List[str]
    audit_frequency: str
    documentation_requirements: List[str]

class ComplianceManager:
    """Manages compliance requirements for AI fraud detection."""
    
    def __init__(self):
        """Initialize compliance manager with default settings."""
        self.requirements = {
            Region.EU: ComplianceRequirement(
                region=Region.EU,
                regulations=["EU_AI_ACT", "GDPR"],
                risk_level=RiskLevel.HIGH,
                required_validations=[
                    "model_bias_check",
                    "data_quality_assessment",
                    "explainability_report"
                ],
                audit_frequency="QUARTERLY",
                documentation_requirements=[
                    "model_documentation",
                    "risk_assessment",
                    "validation_reports"
                ]
            ),
            Region.INDIA: ComplianceRequirement(
                region=Region.INDIA,
                regulations=["RBI_AI_FRAMEWORK", "DPDP"],
                risk_level=RiskLevel.HIGH,
                required_validations=[
                    "model_performance_check",
                    "data_localization_audit",
                    "customer_impact_assessment"
                ],
                audit_frequency="QUARTERLY",
                documentation_requirements=[
                    "ethics_committee_approval",
                    "customer_communication_records",
                    "incident_reports"
                ]
            )
        }
        
        # Model governance settings
        self.model_governance = {
            "validation_frequency": "MONTHLY",
            "required_metrics": [
                "accuracy",
                "false_positive_rate",
                "false_negative_rate",
                "bias_metrics"
            ],
            "explainability_requirements": {
                "local_explanations": True,
                "global_explanations": True,
                "minimum_confidence_threshold": 0.85
            }
        }
        
        # Data governance settings
        self.data_governance = {
            "data_quality_checks": [
                "completeness",
                "accuracy",
                "consistency",
                "timeliness"
            ],
            "data_protection": {
                "encryption_required": True,
                "data_retention_period_days": 365,
                "data_anonymization_required": True
            }
        }
    
    def get_requirements(self, region: Region) -> Optional[ComplianceRequirement]:
        """Get compliance requirements for a specific region."""
        return self.requirements.get(region)
    
    def validate_model_compliance(
        self, 
        region: Region,
        model_metrics: Dict,
        validation_reports: Dict
    ) -> tuple[bool, List[str]]:
        """
        Validate if a model meets compliance requirements for a region.
        
        Args:
            region: Target regulatory region
            model_metrics: Dictionary of model performance metrics
            validation_reports: Dictionary of validation reports
            
        Returns:
            Tuple of (is_compliant, list of compliance issues)
        """
        requirements = self.get_requirements(region)
        if not requirements:
            return False, ["Region not supported"]
            
        issues = []
        
        # Check required metrics
        for metric in self.model_governance["required_metrics"]:
            if metric not in model_metrics:
                issues.append(f"Missing required metric: {metric}")
        
        # Check required validations
        for validation in requirements.required_validations:
            if validation not in validation_reports:
                issues.append(f"Missing required validation: {validation}")
        
        # Check explainability requirements
        if self.model_governance["explainability_requirements"]["local_explanations"]:
            if "local_explanations" not in validation_reports:
                issues.append("Missing local explanations")
        
        return len(issues) == 0, issues
    
    def log_compliance_check(
        self,
        region: Region,
        model_id: str,
        is_compliant: bool,
        issues: List[str]
    ) -> None:
        """Log compliance check results."""
        timestamp = datetime.utcnow().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "region": region.value,
            "model_id": model_id,
            "is_compliant": is_compliant,
            "issues": issues
        }
        logger.info(f"Compliance check: {json.dumps(log_entry)}")
    
    def get_required_documentation(self, region: Region) -> List[str]:
        """Get required documentation for a region."""
        requirements = self.get_requirements(region)
        return requirements.documentation_requirements if requirements else []
