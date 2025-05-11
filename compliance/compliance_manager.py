from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import json
from pathlib import Path
from security.audit_trail import AuditTrail
from security.hsm import HSM
from compliance.compliance_config import COMPLIANCE_CONFIG

class ComplianceError(Exception):
    """Raised when compliance operations fail"""
    pass

class ComplianceManager:
    def __init__(self, config: Dict[str, Any]):
        """Initialize compliance manager with strict requirements"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize security components
        self.hsm = HSM(config)
        self.audit = AuditTrail(config)
        
        # Initialize compliance state
        self.compliance_state = self._initialize_compliance_state()
        
        # Initialize monitoring
        self.monitor = self._initialize_monitoring()
        
        # Initialize reporting
        self.reporter = self._initialize_reporting()
    
    def _initialize_compliance_state(self) -> Dict[str, Any]:
        """Initialize compliance state tracking"""
        try:
            return {
                "standards": self._initialize_standards_state(),
                "controls": self._initialize_controls_state(),
                "violations": [],
                "last_audit": None,
                "status": "INITIALIZING"
            }
        except Exception as e:
            self.logger.error(f"Compliance state initialization failed: {str(e)}")
            raise ComplianceError(f"Failed to initialize compliance state: {str(e)}")
    
    def _initialize_standards_state(self) -> Dict[str, Any]:
        """Initialize compliance standards state"""
        try:
            standards = {}
            for std, config in COMPLIANCE_CONFIG["standards"].items():
                if config["enabled"]:
                    standards[std] = {
                        "version": config["version"],
                        "status": "PENDING",
                        "last_review": None,
                        "requirements": self._initialize_requirements_state(config["requirements"])
                    }
            return standards
        except Exception as e:
            self.logger.error(f"Standards state initialization failed: {str(e)}")
            raise ComplianceError(f"Failed to initialize standards state: {str(e)}")
    
    def _initialize_requirements_state(self, requirements: Dict[str, str]) -> Dict[str, Any]:
        """Initialize requirements state"""
        try:
            req_state = {}
            for req_id, req_desc in requirements.items():
                req_state[req_id] = {
                    "description": req_desc,
                    "status": "PENDING",
                    "last_check": None,
                    "evidence": [],
                    "violations": []
                }
            return req_state
        except Exception as e:
            self.logger.error(f"Requirements state initialization failed: {str(e)}")
            raise ComplianceError(f"Failed to initialize requirements state: {str(e)}")
    
    def _initialize_controls_state(self) -> Dict[str, Any]:
        """Initialize controls state"""
        try:
            controls = {}
            for control, config in COMPLIANCE_CONFIG["requirements"].items():
                controls[control] = {
                    "config": config,
                    "status": "PENDING",
                    "last_check": None,
                    "violations": []
                }
            return controls
        except Exception as e:
            self.logger.error(f"Controls state initialization failed: {str(e)}")
            raise ComplianceError(f"Failed to initialize controls state: {str(e)}")
    
    def _initialize_monitoring(self) -> Dict[str, Any]:
        """Initialize compliance monitoring"""
        try:
            return {
                "schedules": self._initialize_monitoring_schedules(),
                "thresholds": COMPLIANCE_CONFIG["monitoring"]["thresholds"],
                "alerting": COMPLIANCE_CONFIG["monitoring"]["alerting"],
                "status": "ACTIVE"
            }
        except Exception as e:
            self.logger.error(f"Monitoring initialization failed: {str(e)}")
            raise ComplianceError(f"Failed to initialize monitoring: {str(e)}")
    
    def _initialize_monitoring_schedules(self) -> Dict[str, List[str]]:
        """Initialize monitoring schedules"""
        try:
            schedules = {}
            for freq, items in COMPLIANCE_CONFIG["monitoring"]["frequency"].items():
                schedules[freq] = items
            return schedules
        except Exception as e:
            self.logger.error(f"Monitoring schedules initialization failed: {str(e)}")
            raise ComplianceError(f"Failed to initialize monitoring schedules: {str(e)}")
    
    def _initialize_reporting(self) -> Dict[str, Any]:
        """Initialize compliance reporting"""
        try:
            return {
                "templates": self._initialize_report_templates(),
                "schedule": COMPLIANCE_CONFIG["reporting"]["frequency"],
                "last_reports": {},
                "status": "ACTIVE"
            }
        except Exception as e:
            self.logger.error(f"Reporting initialization failed: {str(e)}")
            raise ComplianceError(f"Failed to initialize reporting: {str(e)}")
    
    def _initialize_report_templates(self) -> Dict[str, Any]:
        """Initialize report templates"""
        try:
            templates = {}
            for freq, reports in COMPLIANCE_CONFIG["reporting"]["frequency"].items():
                for report in reports:
                    templates[report] = {
                        "format": COMPLIANCE_CONFIG["reporting"]["formats"],
                        "required_fields": COMPLIANCE_CONFIG["reporting"]["required_fields"],
                        "status": "TEMPLATE_READY"
                    }
            return templates
        except Exception as e:
            self.logger.error(f"Report templates initialization failed: {str(e)}")
            raise ComplianceError(f"Failed to initialize report templates: {str(e)}")
    
    def check_compliance(self) -> Dict[str, Any]:
        """Check overall compliance status"""
        try:
            # Check all standards
            for std in self.compliance_state["standards"]:
                self._check_standard_compliance(std)
            
            # Check all controls
            for control in self.compliance_state["controls"]:
                self._check_control_compliance(control)
            
            # Update compliance status
            self._update_compliance_status()
            
            return self.compliance_state
        except Exception as e:
            self.logger.error(f"Compliance check failed: {str(e)}")
            raise ComplianceError(f"Failed to check compliance: {str(e)}")
    
    def _check_standard_compliance(self, standard: str) -> None:
        """Check compliance for a specific standard"""
        try:
            std_state = self.compliance_state["standards"][standard]
            
            # Check all requirements
            for req_id in std_state["requirements"]:
                self._check_requirement_compliance(standard, req_id)
            
            # Update standard status
            self._update_standard_status(standard)
        except Exception as e:
            self.logger.error(f"Standard {standard} compliance check failed: {str(e)}")
            raise ComplianceError(f"Failed to check {standard} compliance: {str(e)}")
    
    def _check_requirement_compliance(self, standard: str, req_id: str) -> None:
        """Check compliance for a specific requirement"""
        try:
            req_state = self.compliance_state["standards"][standard]["requirements"][req_id]
            
            # Check requirement implementation
            self._check_requirement_implementation(standard, req_id)
            
            # Check requirement evidence
            self._check_requirement_evidence(standard, req_id)
            
            # Update requirement status
            self._update_requirement_status(standard, req_id)
        except Exception as e:
            self.logger.error(f"Requirement {req_id} compliance check failed: {str(e)}")
            raise ComplianceError(f"Failed to check requirement {req_id} compliance: {str(e)}")
    
    def _check_control_compliance(self, control: str) -> None:
        """Check compliance for a specific control"""
        try:
            ctrl_state = self.compliance_state["controls"][control]
            
            # Check control implementation
            self._check_control_implementation(control)
            
            # Check control violations
            self._check_control_violations(control)
            
            # Update control status
            self._update_control_status(control)
        except Exception as e:
            self.logger.error(f"Control {control} compliance check failed: {str(e)}")
            raise ComplianceError(f"Failed to check control {control} compliance: {str(e)}")
    
    def _update_compliance_status(self) -> None:
        """Update overall compliance status"""
        try:
            # Check standards status
            standards_status = all(
                std["status"] == "COMPLIANT"
                for std in self.compliance_state["standards"].values()
            )
            
            # Check controls status
            controls_status = all(
                ctrl["status"] == "COMPLIANT"
                for ctrl in self.compliance_state["controls"].values()
            )
            
            # Update overall status
            if standards_status and controls_status:
                self.compliance_state["status"] = "COMPLIANT"
            elif len(self.compliance_state["violations"]) > 0:
                self.compliance_state["status"] = "NON_COMPLIANT"
            else:
                self.compliance_state["status"] = "PARTIALLY_COMPLIANT"
            
            # Log compliance status
            self.audit.log_event(
                "COMPLIANCE_STATUS_UPDATE",
                {
                    "status": self.compliance_state["status"],
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            self.logger.error(f"Compliance status update failed: {str(e)}")
            raise ComplianceError(f"Failed to update compliance status: {str(e)}")
    
    def generate_report(self, report_type: str, format: str = "json") -> str:
        """Generate compliance report"""
        try:
            # Get report template
            template = self.reporter["templates"][report_type]
            
            # Generate report content
            report_content = self._generate_report_content(report_type)
            
            # Format report
            if format == "json":
                report = json.dumps(report_content, indent=4)
            elif format == "pdf":
                report = self._generate_pdf_report(report_content)
            elif format == "csv":
                report = self._generate_csv_report(report_content)
            else:
                raise ComplianceError(f"Unsupported report format: {format}")
            
            # Store report
            self._store_report(report_type, format, report)
            
            return report
        except Exception as e:
            self.logger.error(f"Report generation failed: {str(e)}")
            raise ComplianceError(f"Failed to generate report: {str(e)}")
    
    def _generate_report_content(self, report_type: str) -> Dict[str, Any]:
        """Generate report content"""
        try:
            content = {
                "report_type": report_type,
                "timestamp": datetime.now().isoformat(),
                "compliance_status": self.compliance_state["status"],
                "standards": self._get_standards_summary(),
                "controls": self._get_controls_summary(),
                "violations": self.compliance_state["violations"]
            }
            
            return content
        except Exception as e:
            self.logger.error(f"Report content generation failed: {str(e)}")
            raise ComplianceError(f"Failed to generate report content: {str(e)}")
    
    def _get_standards_summary(self) -> Dict[str, Any]:
        """Get summary of compliance standards"""
        try:
            summary = {}
            for std, state in self.compliance_state["standards"].items():
                summary[std] = {
                    "version": state["version"],
                    "status": state["status"],
                    "requirements": self._get_requirements_summary(std)
                }
            return summary
        except Exception as e:
            self.logger.error(f"Standards summary failed: {str(e)}")
            raise ComplianceError(f"Failed to get standards summary: {str(e)}")
    
    def _get_requirements_summary(self, standard: str) -> Dict[str, Any]:
        """Get summary of requirements for a standard"""
        try:
            summary = {}
            for req_id, state in self.compliance_state["standards"][standard]["requirements"].items():
                summary[req_id] = {
                    "status": state["status"],
                    "violations": len(state["violations"])
                }
            return summary
        except Exception as e:
            self.logger.error(f"Requirements summary failed: {str(e)}")
            raise ComplianceError(f"Failed to get requirements summary: {str(e)}")
    
    def _get_controls_summary(self) -> Dict[str, Any]:
        """Get summary of controls"""
        try:
            summary = {}
            for ctrl, state in self.compliance_state["controls"].items():
                summary[ctrl] = {
                    "status": state["status"],
                    "violations": len(state["violations"])
                }
            return summary
        except Exception as e:
            self.logger.error(f"Controls summary failed: {str(e)}")
            raise ComplianceError(f"Failed to get controls summary: {str(e)}")
    
    def _store_report(self, report_type: str, format: str, report: str) -> None:
        """Store compliance report"""
        try:
            # Create reports directory if it doesn't exist
            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)
            
            # Create report filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{report_type}_{timestamp}.{format}"
            
            # Store report
            with open(reports_dir / filename, "w") as f:
                f.write(report)
            
            # Update last report
            self.reporter["last_reports"][report_type] = {
                "filename": filename,
                "timestamp": datetime.now().isoformat()
            }
            
            # Log report storage
            self.audit.log_event(
                "REPORT_STORAGE",
                {
                    "report_type": report_type,
                    "format": format,
                    "filename": filename
                }
            )
        except Exception as e:
            self.logger.error(f"Report storage failed: {str(e)}")
            raise ComplianceError(f"Failed to store report: {str(e)}")
