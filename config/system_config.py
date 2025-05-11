"""
System Configuration Parameters

This file contains all configurable parameters for the fraud detection system.
"""

from typing import Dict, Any
import os

class SystemConfig:
    def __init__(self):
        """Initialize system configuration with default values"""
        self.config = {
            # AI Model Parameters
            "model": {
                "primary_model": "claude-3.7-sonnet",
                "backup_model": "gpt-4.5",
                "drift_threshold": 0.05,  # Maximum allowed drift score
                "retraining_threshold": 0.1,  # Threshold for triggering retraining
                "performance_degradation_threshold": 0.05,  # Maximum allowed performance drop
                "validation_interval": 3600,  # Model validation interval in seconds
            },
            
            # Security Parameters
            "security": {
                "encryption": {
                    "algorithm": "AES-256",
                    "key_rotation_days": 90,
                    "key_storage": "HSM",
                    "key_exchange_protocol": "TLS 1.3",
                    "data_at_rest_encryption": True,
                    "data_in_transit_encryption": True
                },
                "audit": {
                    "log_retention_days": 365,
                    "log_rotation_days": 7,
                    "audit_frequency": "daily"
                }
            },
            
            # Compliance Parameters
            "compliance": {
                "gdpr": {
                    "data_retention_days": {
                        "transaction_data": 90,
                        "audit_logs": 365,
                        "personal_data": 180
                    },
                    "data_minimization": {
                        "max_fields": 10,
                        "required_fields": ["timestamp", "amount", "customer_id"]
                    }
                },
                "dpdp": {
                    "data_localization": {
                        "allowed_countries": ["India"],
                        "exceptions": ["backup", "disaster_recovery"]
                    },
                    "consent": {
                        "validity_days": 365,
                        "review_frequency": "monthly"
                    }
                }
            },
            
            # Monitoring Parameters
            "monitoring": {
                "thresholds": {
                    "error_rate": 0.01,  # Maximum allowed error rate
                    "latency": {
                        "warning": 500,  # Warning threshold in ms
                        "critical": 1000  # Critical threshold in ms
                    },
                    "performance": {
                        "accuracy_drop": 0.05,
                        "recall_drop": 0.1
                    }
                },
                "alerting": {
                    "escalation_level": "critical",
                    "notification_channels": ["email", "slack"],
                    "response_time": 300  # Response time in seconds
                }
            },
            
            # Bias Detection Parameters
            "bias": {
                "thresholds": {
                    "statistical_significance": 0.05,
                    "demographic_disparity": 0.1,
                    "minimum_sample_size": 30,
                    "outlier_threshold": 0.05
                },
                "correction": {
                    "methods": ["reweighting", "preprocessing"],
                    "trigger_threshold": 0.2
                }
            },
            
            # RBAC Parameters
            "rbac": {
                "roles": {
                    "admin": {
                        "permissions": ["all"],
                        "review_frequency": "quarterly"
                    },
                    "analyst": {
                        "permissions": ["read", "flag", "review"],
                        "review_frequency": "monthly"
                    },
                    "reviewer": {
                        "permissions": ["review", "approve"],
                        "review_frequency": "weekly"
                    }
                },
                "separation": {
                    "required": True,
                    "minimum_roles": 2,
                    "review_period": 30  # Days
                }
            },
            
            # Human-in-the-Loop Parameters
            "human_in_loop": {
                "flagging": {
                    "threshold": 0.7,
                    "review_sla": 24,  # Hours
                    "escalation_threshold": 0.9
                },
                "review": {
                    "qualification": {
                        "certifications": ["CFA", "CPA"],
                        "experience": 2  # Years
                    },
                    "documentation": {
                        "required": True,
                        "retention_days": 365
                    }
                }
            },
            
            # Data Privacy Parameters
            "privacy": {
                "data_masking": {
                    "sensitive_fields": ["ssn", "credit_card", "phone"],
                    "masking_type": "partial"
                },
                "pseudonymization": {
                    "enabled": True,
                    "algorithm": "hash",
                    "salt_rotation_days": 30
                },
                "audit": {
                    "required": True,
                    "log_retention_days": 365,
                    "review_frequency": "monthly"
                },
                "breach": {
                    "notification_hours": 24,
                    "response_plan": "emergency",
                    "escalation_level": "critical"
                }
            }
        }
    
    def get_config(self) -> Dict[str, Any]:
        """Get the complete configuration"""
        return self.config
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get a specific configuration section"""
        return self.config.get(section, {})
    
    def validate_config(self) -> bool:
        """Validate the configuration"""
        required_sections = [
            "model", "security", "compliance", "monitoring", "bias",
            "rbac", "human_in_loop", "privacy"
        ]
        
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")
        
        return True
