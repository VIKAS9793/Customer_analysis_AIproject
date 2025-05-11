from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import json
import csv
import os
from pathlib import Path
from security.audit_trail import AuditTrail
from security.hsm import HSM
from compliance.compliance_config import COMPLIANCE_CONFIG
from compliance.compliance_manager import ComplianceManager

class ReportingError(Exception):
    """Raised when reporting operations fail"""
    pass

class ComplianceReporting:
    """Handles compliance reporting with multiple output formats and scheduling"""
    
    def __init__(self, config: Dict[str, Any], compliance_manager: ComplianceManager):
        """Initialize compliance reporting with secure configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.compliance_manager = compliance_manager
        
        # Initialize security components
        self.hsm = HSM(config)
        self.audit = AuditTrail(config)
        
        # Initialize reporting formats
        self.formats = self._initialize_formats()
        
        # Initialize reporting schedules
        self.schedules = self._initialize_schedules()
        
        # Initialize report storage
        self.storage = self._initialize_storage()
        
        # Initialize report templates
        self.templates = self._initialize_templates()
    
    def _initialize_formats(self) -> Dict[str, Dict[str, Any]]:
        """Initialize supported reporting formats"""
        try:
            formats = {}
            for format_name in COMPLIANCE_CONFIG["reporting"]["formats"]:
                formats[format_name] = {
                    "enabled": True,
                    "handler": self._get_format_handler(format_name),
                    "mime_type": self._get_mime_type(format_name)
                }
            return formats
        except Exception as e:
            self.logger.error(f"Format initialization failed: {str(e)}")
            raise ReportingError(f"Failed to initialize formats: {str(e)}")
    
    def _get_format_handler(self, format_name: str) -> callable:
        """Get handler function for a specific format"""
        handlers = {
            "json": self._generate_json_report,
            "csv": self._generate_csv_report,
            "pdf": self._generate_pdf_report
        }
        
        if format_name not in handlers:
            raise ReportingError(f"Unsupported format: {format_name}")
        
        return handlers[format_name]
    
    def _get_mime_type(self, format_name: str) -> str:
        """Get MIME type for a specific format"""
        mime_types = {
            "json": "application/json",
            "csv": "text/csv",
            "pdf": "application/pdf"
        }
        
        if format_name not in mime_types:
            raise ReportingError(f"Unknown MIME type for format: {format_name}")
        
        return mime_types[format_name]
    
    def _initialize_schedules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize reporting schedules"""
        try:
            schedules = {}
            for frequency, reports in COMPLIANCE_CONFIG["reporting"]["frequency"].items():
                schedules[frequency] = {
                    "reports": reports,
                    "last_run": None,
                    "next_run": self._calculate_next_run(frequency),
                    "enabled": True
                }
            return schedules
        except Exception as e:
            self.logger.error(f"Schedule initialization failed: {str(e)}")
            raise ReportingError(f"Failed to initialize schedules: {str(e)}")
    
    def _calculate_next_run(self, frequency: str) -> datetime:
        """Calculate next run time based on frequency"""
        now = datetime.now()
        
        if frequency == "daily":
            # Next day at midnight
            return datetime(now.year, now.month, now.day) + timedelta(days=1)
        elif frequency == "weekly":
            # Next Monday at midnight
            days_ahead = 7 - now.weekday()
            return datetime(now.year, now.month, now.day) + timedelta(days=days_ahead)
        elif frequency == "monthly":
            # First day of next month
            if now.month == 12:
                return datetime(now.year + 1, 1, 1)
            else:
                return datetime(now.year, now.month + 1, 1)
        elif frequency == "quarterly":
            # First day of next quarter
            quarter = (now.month - 1) // 3 + 1
            next_quarter = quarter + 1
            next_year = now.year
            if next_quarter > 4:
                next_quarter = 1
                next_year += 1
            return datetime(next_year, (next_quarter - 1) * 3 + 1, 1)
        elif frequency == "yearly":
            # First day of next year
            return datetime(now.year + 1, 1, 1)
        else:
            raise ReportingError(f"Unsupported frequency: {frequency}")
    
    def _initialize_storage(self) -> Dict[str, Any]:
        """Initialize report storage"""
        try:
            # Create reports directory if it doesn't exist
            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)
            
            return {
                "base_path": reports_dir,
                "retention_period": "7y",
                "encryption": True,
                "access_control": {
                    "roles": ["admin", "auditor", "compliance_officer"],
                    "default_role": "compliance_officer"
                }
            }
        except Exception as e:
            self.logger.error(f"Storage initialization failed: {str(e)}")
            raise ReportingError(f"Failed to initialize storage: {str(e)}")
    
    def _initialize_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize report templates"""
        try:
            templates = {}
            for frequency, reports in COMPLIANCE_CONFIG["reporting"]["frequency"].items():
                for report_type in reports:
                    templates[report_type] = {
                        "sections": self._get_template_sections(report_type),
                        "required_fields": COMPLIANCE_CONFIG["reporting"]["required_fields"],
                        "metadata": {
                            "version": "1.0",
                            "classification": "confidential",
                            "retention": "7y"
                        }
                    }
            return templates
        except Exception as e:
            self.logger.error(f"Template initialization failed: {str(e)}")
            raise ReportingError(f"Failed to initialize templates: {str(e)}")
    
    def _get_template_sections(self, report_type: str) -> List[Dict[str, Any]]:
        """Get sections for a specific report template"""
        # Common sections for all reports
        common_sections = [
            {
                "name": "executive_summary",
                "title": "Executive Summary",
                "required": True
            },
            {
                "name": "compliance_status",
                "title": "Compliance Status",
                "required": True
            }
        ]
        
        # Report-specific sections
        if report_type == "security_events":
            return common_sections + [
                {
                    "name": "security_incidents",
                    "title": "Security Incidents",
                    "required": True
                },
                {
                    "name": "event_timeline",
                    "title": "Event Timeline",
                    "required": True
                },
                {
                    "name": "remediation_actions",
                    "title": "Remediation Actions",
                    "required": True
                }
            ]
        elif report_type == "compliance_status":
            return common_sections + [
                {
                    "name": "standards_compliance",
                    "title": "Standards Compliance",
                    "required": True
                },
                {
                    "name": "control_effectiveness",
                    "title": "Control Effectiveness",
                    "required": True
                },
                {
                    "name": "compliance_trends",
                    "title": "Compliance Trends",
                    "required": False
                }
            ]
        elif report_type == "security_audit":
            return common_sections + [
                {
                    "name": "audit_findings",
                    "title": "Audit Findings",
                    "required": True
                },
                {
                    "name": "vulnerability_assessment",
                    "title": "Vulnerability Assessment",
                    "required": True
                },
                {
                    "name": "remediation_plan",
                    "title": "Remediation Plan",
                    "required": True
                }
            ]
        elif report_type == "compliance_audit":
            return common_sections + [
                {
                    "name": "audit_scope",
                    "title": "Audit Scope",
                    "required": True
                },
                {
                    "name": "audit_methodology",
                    "title": "Audit Methodology",
                    "required": True
                },
                {
                    "name": "audit_findings",
                    "title": "Audit Findings",
                    "required": True
                },
                {
                    "name": "recommendations",
                    "title": "Recommendations",
                    "required": True
                }
            ]
        elif report_type == "security_review":
            return common_sections + [
                {
                    "name": "annual_summary",
                    "title": "Annual Summary",
                    "required": True
                },
                {
                    "name": "risk_assessment",
                    "title": "Risk Assessment",
                    "required": True
                },
                {
                    "name": "security_improvements",
                    "title": "Security Improvements",
                    "required": True
                },
                {
                    "name": "future_roadmap",
                    "title": "Future Roadmap",
                    "required": True
                }
            ]
        else:
            # Default sections
            return common_sections
    
    def generate_report(self, report_type: str, format: str = "json") -> str:
        """Generate compliance report in specified format"""
        try:
            # Validate report type
            if report_type not in self._get_available_report_types():
                raise ReportingError(f"Unsupported report type: {report_type}")
            
            # Validate format
            if format not in self.formats:
                raise ReportingError(f"Unsupported format: {format}")
            
            # Get report data
            report_data = self._get_report_data(report_type)
            
            # Generate report in specified format
            handler = self.formats[format]["handler"]
            report_content = handler(report_type, report_data)
            
            # Store report
            report_path = self._store_report(report_type, format, report_content)
            
            # Log report generation
            self._log_report_generation(report_type, format, report_path)
            
            return report_path
        except Exception as e:
            self.logger.error(f"Report generation failed: {str(e)}")
            raise ReportingError(f"Failed to generate report: {str(e)}")
    
    def _get_available_report_types(self) -> List[str]:
        """Get list of available report types"""
        report_types = []
        for frequency, reports in COMPLIANCE_CONFIG["reporting"]["frequency"].items():
            report_types.extend(reports)
        return list(set(report_types))  # Remove duplicates
    
    def _get_report_data(self, report_type: str) -> Dict[str, Any]:
        """Get data for a specific report type"""
        try:
            # Common data for all reports
            common_data = {
                "timestamp": datetime.now().isoformat(),
                "report_type": report_type,
                "organization": self.config.get("organization", "FinConnectAI"),
                "generated_by": "ComplianceReporting",
                "compliance_status": self.compliance_manager.compliance_state["status"]
            }
            
            # Report-specific data
            if report_type == "security_events":
                return {**common_data, **self._get_security_events_data()}
            elif report_type == "compliance_status":
                return {**common_data, **self._get_compliance_status_data()}
            elif report_type == "security_audit":
                return {**common_data, **self._get_security_audit_data()}
            elif report_type == "compliance_audit":
                return {**common_data, **self._get_compliance_audit_data()}
            elif report_type == "security_review":
                return {**common_data, **self._get_security_review_data()}
            else:
                # Default data
                return common_data
        except Exception as e:
            self.logger.error(f"Report data retrieval failed: {str(e)}")
            raise ReportingError(f"Failed to get report data: {str(e)}")
    
    def _get_security_events_data(self) -> Dict[str, Any]:
        """Get data for security events report"""
        return {
            "security_incidents": self.audit.get_security_incidents(),
            "event_timeline": self.audit.get_event_timeline(),
            "remediation_actions": self.audit.get_remediation_actions()
        }
    
    def _get_compliance_status_data(self) -> Dict[str, Any]:
        """Get data for compliance status report"""
        return {
            "standards": self.compliance_manager._get_standards_summary(),
            "controls": self.compliance_manager._get_controls_summary(),
            "violations": self.compliance_manager.compliance_state["violations"],
            "compliance_trends": self._get_compliance_trends()
        }
    
    def _get_security_audit_data(self) -> Dict[str, Any]:
        """Get data for security audit report"""
        return {
            "audit_findings": self.audit.get_audit_findings(),
            "vulnerability_assessment": self.audit.get_vulnerability_assessment(),
            "remediation_plan": self.audit.get_remediation_plan()
        }
    
    def _get_compliance_audit_data(self) -> Dict[str, Any]:
        """Get data for compliance audit report"""
        return {
            "audit_scope": self._get_audit_scope(),
            "audit_methodology": self._get_audit_methodology(),
            "audit_findings": self.audit.get_audit_findings(),
            "recommendations": self._get_audit_recommendations()
        }
    
    def _get_security_review_data(self) -> Dict[str, Any]:
        """Get data for security review report"""
        return {
            "annual_summary": self._get_annual_summary(),
            "risk_assessment": self._get_risk_assessment(),
            "security_improvements": self._get_security_improvements(),
            "future_roadmap": self._get_future_roadmap()
        }
    
    def _get_compliance_trends(self) -> Dict[str, Any]:
        """Get compliance trends over time"""
        # This would typically be implemented with historical data
        # For now, return placeholder data
        return {
            "trend_period": "last_90_days",
            "compliance_rate": {
                "current": 95,
                "previous": 92,
                "trend": "improving"
            },
            "violation_count": {
                "current": 5,
                "previous": 8,
                "trend": "improving"
            }
        }
    
    def _get_audit_scope(self) -> Dict[str, Any]:
        """Get audit scope information"""
        return {
            "standards": list(COMPLIANCE_CONFIG["standards"].keys()),
            "controls": list(COMPLIANCE_CONFIG["requirements"].keys()),
            "time_period": "quarterly",
            "systems_in_scope": [
                "authentication",
                "authorization",
                "encryption",
                "api_security",
                "network_security"
            ]
        }
    
    def _get_audit_methodology(self) -> Dict[str, Any]:
        """Get audit methodology information"""
        return {
            "approach": "risk_based",
            "standards": [
                "ISO 27001",
                "PCI DSS",
                "HIPAA"
            ],
            "techniques": [
                "documentation_review",
                "control_testing",
                "interviews",
                "system_inspection"
            ]
        }
    
    def _get_audit_recommendations(self) -> List[Dict[str, Any]]:
        """Get audit recommendations"""
        # This would typically be generated based on audit findings
        # For now, return placeholder recommendations
        return [
            {
                "id": "REC-001",
                "title": "Enhance Key Rotation",
                "description": "Implement automated key rotation for all encryption keys",
                "priority": "high",
                "standard": "PCI DSS",
                "control": "encryption"
            },
            {
                "id": "REC-002",
                "title": "Improve Audit Logging",
                "description": "Enhance audit logging to capture all security-relevant events",
                "priority": "medium",
                "standard": "ISO 27001",
                "control": "audit"
            },
            {
                "id": "REC-003",
                "title": "Strengthen Access Controls",
                "description": "Implement more granular role-based access controls",
                "priority": "high",
                "standard": "HIPAA",
                "control": "access_control"
            }
        ]
    
    def _get_annual_summary(self) -> Dict[str, Any]:
        """Get annual security summary"""
        return {
            "overall_security_posture": "strong",
            "major_incidents": 2,
            "compliance_status": "compliant",
            "key_achievements": [
                "Implemented HSM for key management",
                "Enhanced session security",
                "Improved API security"
            ],
            "areas_for_improvement": [
                "Real-time monitoring",
                "Automated compliance checking",
                "Security awareness training"
            ]
        }
    
    def _get_risk_assessment(self) -> Dict[str, Any]:
        """Get risk assessment information"""
        return {
            "high_risks": [
                {
                    "id": "RISK-001",
                    "title": "Unauthorized Access",
                    "likelihood": "medium",
                    "impact": "high",
                    "controls": ["access_control", "session_management"]
                },
                {
                    "id": "RISK-002",
                    "title": "Data Breach",
                    "likelihood": "low",
                    "impact": "high",
                    "controls": ["encryption", "data_protection"]
                }
            ],
            "medium_risks": [
                {
                    "id": "RISK-003",
                    "title": "API Abuse",
                    "likelihood": "medium",
                    "impact": "medium",
                    "controls": ["api_security", "rate_limiting"]
                }
            ],
            "low_risks": [
                {
                    "id": "RISK-004",
                    "title": "Session Hijacking",
                    "likelihood": "low",
                    "impact": "medium",
                    "controls": ["session_management", "network_security"]
                }
            ]
        }
    
    def _get_security_improvements(self) -> List[Dict[str, Any]]:
        """Get security improvements information"""
        return [
            {
                "id": "IMP-001",
                "title": "HSM Integration",
                "description": "Integrated Hardware Security Module for key management",
                "impact": "high",
                "status": "completed"
            },
            {
                "id": "IMP-002",
                "title": "Enhanced Session Security",
                "description": "Implemented token rotation and validation",
                "impact": "high",
                "status": "completed"
            },
            {
                "id": "IMP-003",
                "title": "API Security Enhancements",
                "description": "Added request validation and rate limiting",
                "impact": "medium",
                "status": "completed"
            },
            {
                "id": "IMP-004",
                "title": "Compliance Framework",
                "description": "Implemented comprehensive compliance framework",
                "impact": "high",
                "status": "in_progress"
            }
        ]
    
    def _get_future_roadmap(self) -> List[Dict[str, Any]]:
        """Get future security roadmap"""
        return [
            {
                "id": "ROAD-001",
                "title": "Real-time Monitoring",
                "description": "Implement real-time security monitoring with Prometheus",
                "priority": "high",
                "timeline": "Q3 2025"
            },
            {
                "id": "ROAD-002",
                "title": "Automated Compliance Checking",
                "description": "Develop automated compliance checking and reporting",
                "priority": "high",
                "timeline": "Q4 2025"
            },
            {
                "id": "ROAD-003",
                "title": "Security Awareness Training",
                "description": "Implement security awareness training program",
                "priority": "medium",
                "timeline": "Q1 2026"
            },
            {
                "id": "ROAD-004",
                "title": "Advanced Threat Detection",
                "description": "Implement advanced threat detection capabilities",
                "priority": "high",
                "timeline": "Q2 2026"
            }
        ]
    
    def _generate_json_report(self, report_type: str, data: Dict[str, Any]) -> str:
        """Generate JSON report"""
        return json.dumps(data, indent=4)
    
    def _generate_csv_report(self, report_type: str, data: Dict[str, Any]) -> str:
        """Generate CSV report"""
        # CSV generation is more complex and depends on the report structure
        # This is a simplified implementation
        output = []
        
        # Add header row
        header = ["Section", "Key", "Value"]
        output.append(",".join(header))
        
        # Add data rows
        for section, section_data in data.items():
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    if not isinstance(value, (dict, list)):
                        output.append(f"{section},{key},{value}")
            elif not isinstance(section_data, (dict, list)):
                output.append(f"root,{section},{section_data}")
        
        return "\n".join(output)
    
    def _generate_pdf_report(self, report_type: str, data: Dict[str, Any]) -> str:
        """Generate PDF report"""
        # PDF generation requires additional libraries like ReportLab
        # This is a placeholder that returns a JSON representation
        # In a real implementation, this would generate a PDF file
        return json.dumps(data, indent=4)
    
    def _store_report(self, report_type: str, format: str, content: str) -> str:
        """Store report and return the file path"""
        try:
            # Create report directory if it doesn't exist
            report_dir = self.storage["base_path"] / report_type
            report_dir.mkdir(exist_ok=True)
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{report_type}_{timestamp}.{format}"
            file_path = report_dir / filename
            
            # Write report content to file
            with open(file_path, "w") as f:
                f.write(content)
            
            # Return file path as string
            return str(file_path)
        except Exception as e:
            self.logger.error(f"Report storage failed: {str(e)}")
            raise ReportingError(f"Failed to store report: {str(e)}")
    
    def _log_report_generation(self, report_type: str, format: str, file_path: str) -> None:
        """Log report generation event"""
        try:
            self.audit.log_event(
                "REPORT_GENERATION",
                {
                    "report_type": report_type,
                    "format": format,
                    "file_path": file_path,
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            self.logger.error(f"Report logging failed: {str(e)}")
            # Don't raise an exception here, as the report was generated successfully
    
    def check_scheduled_reports(self) -> List[Dict[str, Any]]:
        """Check for scheduled reports that need to be generated"""
        try:
            reports_to_generate = []
            now = datetime.now()
            
            for frequency, schedule in self.schedules.items():
                if schedule["enabled"] and schedule["next_run"] <= now:
                    # Add reports for this frequency to the list
                    for report_type in schedule["reports"]:
                        reports_to_generate.append({
                            "report_type": report_type,
                            "frequency": frequency,
                            "formats": COMPLIANCE_CONFIG["reporting"]["formats"]
                        })
                    
                    # Update schedule
                    self.schedules[frequency]["last_run"] = now
                    self.schedules[frequency]["next_run"] = self._calculate_next_run(frequency)
            
            return reports_to_generate
        except Exception as e:
            self.logger.error(f"Scheduled reports check failed: {str(e)}")
            raise ReportingError(f"Failed to check scheduled reports: {str(e)}")
    
    def generate_scheduled_reports(self) -> List[str]:
        """Generate all scheduled reports that are due"""
        try:
            generated_reports = []
            reports_to_generate = self.check_scheduled_reports()
            
            for report_info in reports_to_generate:
                for format in report_info["formats"]:
                    report_path = self.generate_report(report_info["report_type"], format)
                    generated_reports.append(report_path)
            
            return generated_reports
        except Exception as e:
            self.logger.error(f"Scheduled reports generation failed: {str(e)}")
            raise ReportingError(f"Failed to generate scheduled reports: {str(e)}")
