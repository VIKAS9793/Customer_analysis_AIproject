from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import uuid
from security.audit_trail import AuditTrail
from security.hsm import HSM
from compliance.compliance_config import COMPLIANCE_CONFIG
from compliance.compliance_manager import ComplianceManager

class AuditError(Exception):
    """Raised when audit operations fail"""
    pass

class AuditProcedures:
    """Handles compliance audit procedures and findings management"""
    
    def __init__(self, config: Dict[str, Any], compliance_manager: ComplianceManager):
        """Initialize audit procedures with secure configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.compliance_manager = compliance_manager
        
        # Initialize security components
        self.hsm = HSM(config)
        self.audit_trail = AuditTrail(config)
        
        # Initialize audit state
        self.audit_state = self._initialize_audit_state()
        
        # Initialize audit schedules
        self.audit_schedules = self._initialize_audit_schedules()
        
        # Initialize audit findings
        self.audit_findings = self._initialize_audit_findings()
        
        # Initialize audit remediation
        self.audit_remediation = self._initialize_audit_remediation()
    
    def _initialize_audit_state(self) -> Dict[str, Any]:
        """Initialize audit state tracking"""
        try:
            return {
                "current_audits": {},
                "completed_audits": {},
                "audit_history": [],
                "last_audit": None,
                "status": "ACTIVE"
            }
        except Exception as e:
            self.logger.error(f"Audit state initialization failed: {str(e)}")
            raise AuditError(f"Failed to initialize audit state: {str(e)}")
    
    def _initialize_audit_schedules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize audit schedules for different standards"""
        try:
            schedules = {}
            for standard, config in COMPLIANCE_CONFIG["standards"].items():
                if config["enabled"]:
                    schedules[standard] = {
                        "frequency": self._get_audit_frequency(standard),
                        "last_audit": None,
                        "next_audit": self._calculate_next_audit(standard),
                        "scope": self._get_audit_scope(standard),
                        "status": "SCHEDULED"
                    }
            
            # Add SOC2 schedule (as specified in the configuration)
            schedules["soc2"] = {
                "frequency": "semi-annual",
                "last_audit": None,
                "next_audit": self._calculate_next_audit("soc2"),
                "scope": self._get_audit_scope("soc2"),
                "status": "SCHEDULED"
            }
            
            # Add GDPR schedule (as specified in the configuration)
            schedules["gdpr"] = {
                "frequency": "annual",
                "last_audit": None,
                "next_audit": self._calculate_next_audit("gdpr"),
                "scope": self._get_audit_scope("gdpr"),
                "status": "SCHEDULED"
            }
            
            return schedules
        except Exception as e:
            self.logger.error(f"Audit schedules initialization failed: {str(e)}")
            raise AuditError(f"Failed to initialize audit schedules: {str(e)}")
    
    def _get_audit_frequency(self, standard: str) -> str:
        """Get audit frequency for a standard"""
        if standard == "pci_dss":
            return "quarterly"
        elif standard == "iso_27001":
            return "annual"
        elif standard == "hipaa":
            return "annual"
        elif standard == "soc2":
            return "semi-annual"
        elif standard == "gdpr":
            return "annual"
        else:
            return "annual"
    
    def _calculate_next_audit(self, standard: str) -> str:
        """Calculate next audit date based on frequency"""
        now = datetime.now()
        frequency = self._get_audit_frequency(standard)
        
        if frequency == "monthly":
            next_month = now.month + 1 if now.month < 12 else 1
            next_year = now.year if now.month < 12 else now.year + 1
            next_audit = datetime(next_year, next_month, 1)
        elif frequency == "quarterly":
            current_quarter = (now.month - 1) // 3 + 1
            next_quarter = current_quarter + 1 if current_quarter < 4 else 1
            next_year = now.year if current_quarter < 4 else now.year + 1
            next_audit = datetime(next_year, (next_quarter - 1) * 3 + 1, 1)
        elif frequency == "semi-annual":
            if now.month < 7:
                next_audit = datetime(now.year, 7, 1)
            else:
                next_audit = datetime(now.year + 1, 1, 1)
        elif frequency == "annual":
            next_audit = datetime(now.year + 1, 1, 1)
        else:
            # Default to annual
            next_audit = datetime(now.year + 1, 1, 1)
        
        return next_audit.isoformat()
    
    def _get_audit_scope(self, standard: str) -> Dict[str, Any]:
        """Get audit scope for a standard"""
        common_scope = {
            "systems": [
                "authentication",
                "authorization",
                "encryption",
                "api_security",
                "network_security",
                "data_protection"
            ],
            "data_categories": [
                "customer_data",
                "transaction_data",
                "authentication_data",
                "system_logs"
            ]
        }
        
        if standard == "pci_dss":
            return {
                **common_scope,
                "specific_requirements": [
                    "cardholder_data_protection",
                    "secure_network",
                    "vulnerability_management",
                    "access_control",
                    "network_monitoring",
                    "security_policy"
                ]
            }
        elif standard == "iso_27001":
            return {
                **common_scope,
                "specific_requirements": [
                    "information_security_policy",
                    "organization_of_information_security",
                    "human_resource_security",
                    "asset_management",
                    "access_control",
                    "cryptography"
                ]
            }
        elif standard == "hipaa":
            return {
                **common_scope,
                "specific_requirements": [
                    "administrative_safeguards",
                    "physical_safeguards",
                    "technical_safeguards",
                    "breach_notification"
                ]
            }
        elif standard == "soc2":
            return {
                **common_scope,
                "specific_requirements": [
                    "security",
                    "availability",
                    "processing_integrity",
                    "confidentiality",
                    "privacy"
                ]
            }
        elif standard == "gdpr":
            return {
                **common_scope,
                "specific_requirements": [
                    "lawful_processing",
                    "consent_management",
                    "data_subject_rights",
                    "data_protection",
                    "breach_notification",
                    "data_processing_records"
                ]
            }
        else:
            return common_scope
    
    def _initialize_audit_findings(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize audit findings tracking"""
        try:
            findings = {}
            for standard in self.audit_schedules.keys():
                findings[standard] = []
            return findings
        except Exception as e:
            self.logger.error(f"Audit findings initialization failed: {str(e)}")
            raise AuditError(f"Failed to initialize audit findings: {str(e)}")
    
    def _initialize_audit_remediation(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize audit remediation tracking"""
        try:
            remediation = {}
            for standard in self.audit_schedules.keys():
                remediation[standard] = []
            return remediation
        except Exception as e:
            self.logger.error(f"Audit remediation initialization failed: {str(e)}")
            raise AuditError(f"Failed to initialize audit remediation: {str(e)}")
    
    def schedule_audit(self, standard: str, date: str = None) -> Dict[str, Any]:
        """Schedule an audit for a specific standard"""
        try:
            # Validate standard
            self._validate_standard(standard)
            
            # Set audit date
            audit_date = datetime.fromisoformat(date) if date else datetime.now()
            
            # Generate audit ID
            audit_id = self._generate_audit_id(standard)
            
            # Create audit
            audit = {
                "id": audit_id,
                "standard": standard,
                "scheduled_date": audit_date.isoformat(),
                "status": "SCHEDULED",
                "scope": self.audit_schedules[standard]["scope"],
                "auditor": "INTERNAL",  # Default to internal auditor
                "findings": [],
                "remediation": []
            }
            
            # Add to current audits
            self.audit_state["current_audits"][audit_id] = audit
            
            # Update audit schedule
            self.audit_schedules[standard]["next_audit"] = audit_date.isoformat()
            self.audit_schedules[standard]["status"] = "SCHEDULED"
            
            # Log audit scheduling
            self._log_audit_event(standard, "AUDIT_SCHEDULED", {
                "audit_id": audit_id,
                "scheduled_date": audit_date.isoformat()
            })
            
            return audit
        except Exception as e:
            self.logger.error(f"Audit scheduling failed: {str(e)}")
            raise AuditError(f"Failed to schedule audit: {str(e)}")
    
    def _validate_standard(self, standard: str) -> None:
        """Validate if a standard is supported and enabled"""
        if standard not in self.audit_schedules:
            if standard in COMPLIANCE_CONFIG["standards"] and not COMPLIANCE_CONFIG["standards"][standard]["enabled"]:
                raise AuditError(f"Standard {standard} is not enabled")
            else:
                raise AuditError(f"Unsupported standard: {standard}")
    
    def _generate_audit_id(self, standard: str) -> str:
        """Generate unique audit ID"""
        try:
            # Create a unique ID based on standard and timestamp
            unique_string = f"{standard}_{datetime.now().isoformat()}"
            
            # Generate UUID based on the unique string
            namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # Namespace for URLs
            audit_id = str(uuid.uuid5(namespace, unique_string))
            
            return audit_id
        except Exception as e:
            self.logger.error(f"Audit ID generation failed: {str(e)}")
            raise AuditError(f"Failed to generate audit ID: {str(e)}")
    
    def start_audit(self, audit_id: str) -> Dict[str, Any]:
        """Start a scheduled audit"""
        try:
            # Check if audit exists
            if audit_id not in self.audit_state["current_audits"]:
                raise AuditError(f"Audit {audit_id} not found")
            
            # Get audit
            audit = self.audit_state["current_audits"][audit_id]
            
            # Check if audit is in correct state
            if audit["status"] != "SCHEDULED":
                raise AuditError(f"Audit {audit_id} is not in SCHEDULED state")
            
            # Update audit status
            audit["status"] = "IN_PROGRESS"
            audit["start_date"] = datetime.now().isoformat()
            
            # Update audit schedule
            self.audit_schedules[audit["standard"]]["status"] = "IN_PROGRESS"
            
            # Log audit start
            self._log_audit_event(audit["standard"], "AUDIT_STARTED", {
                "audit_id": audit_id,
                "start_date": audit["start_date"]
            })
            
            return audit
        except Exception as e:
            self.logger.error(f"Audit start failed: {str(e)}")
            raise AuditError(f"Failed to start audit: {str(e)}")
    
    def add_audit_finding(self, audit_id: str, finding: Dict[str, Any]) -> str:
        """Add a finding to an audit"""
        try:
            # Check if audit exists
            if audit_id not in self.audit_state["current_audits"]:
                raise AuditError(f"Audit {audit_id} not found")
            
            # Get audit
            audit = self.audit_state["current_audits"][audit_id]
            
            # Check if audit is in correct state
            if audit["status"] != "IN_PROGRESS":
                raise AuditError(f"Audit {audit_id} is not in IN_PROGRESS state")
            
            # Generate finding ID
            finding_id = self._generate_finding_id(audit_id)
            
            # Prepare finding
            prepared_finding = {
                "id": finding_id,
                "timestamp": datetime.now().isoformat(),
                "severity": finding.get("severity", "medium"),
                "title": finding.get("title", "Unnamed Finding"),
                "description": finding.get("description", ""),
                "requirement": finding.get("requirement", ""),
                "status": "OPEN",
                "remediation_plan": None,
                "remediation_status": "NOT_STARTED"
            }
            
            # Add finding to audit
            audit["findings"].append(prepared_finding)
            
            # Add finding to findings tracking
            self.audit_findings[audit["standard"]].append(prepared_finding)
            
            # Log finding
            self._log_audit_event(audit["standard"], "AUDIT_FINDING_ADDED", {
                "audit_id": audit_id,
                "finding_id": finding_id,
                "severity": prepared_finding["severity"]
            })
            
            return finding_id
        except Exception as e:
            self.logger.error(f"Audit finding addition failed: {str(e)}")
            raise AuditError(f"Failed to add audit finding: {str(e)}")
    
    def _generate_finding_id(self, audit_id: str) -> str:
        """Generate unique finding ID"""
        try:
            # Create a unique ID based on audit ID and timestamp
            unique_string = f"{audit_id}_{datetime.now().isoformat()}"
            
            # Generate UUID based on the unique string
            namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # Namespace for URLs
            finding_id = str(uuid.uuid5(namespace, unique_string))
            
            return finding_id
        except Exception as e:
            self.logger.error(f"Finding ID generation failed: {str(e)}")
            raise AuditError(f"Failed to generate finding ID: {str(e)}")
    
    def add_remediation_plan(self, audit_id: str, finding_id: str, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Add a remediation plan for a finding"""
        try:
            # Check if audit exists
            if audit_id not in self.audit_state["current_audits"]:
                raise AuditError(f"Audit {audit_id} not found")
            
            # Get audit
            audit = self.audit_state["current_audits"][audit_id]
            
            # Find the finding
            finding = next((f for f in audit["findings"] if f["id"] == finding_id), None)
            if finding is None:
                raise AuditError(f"Finding {finding_id} not found in audit {audit_id}")
            
            # Prepare remediation plan
            remediation_plan = {
                "id": str(uuid.uuid4()),
                "finding_id": finding_id,
                "description": plan.get("description", ""),
                "action_items": plan.get("action_items", []),
                "owner": plan.get("owner", ""),
                "target_date": plan.get("target_date", (datetime.now() + timedelta(days=30)).isoformat()),
                "status": "OPEN",
                "completion_date": None
            }
            
            # Update finding
            finding["remediation_plan"] = remediation_plan["id"]
            finding["remediation_status"] = "PLANNED"
            
            # Add remediation plan to audit
            audit["remediation"].append(remediation_plan)
            
            # Add remediation plan to remediation tracking
            self.audit_remediation[audit["standard"]].append(remediation_plan)
            
            # Log remediation plan
            self._log_audit_event(audit["standard"], "REMEDIATION_PLAN_ADDED", {
                "audit_id": audit_id,
                "finding_id": finding_id,
                "remediation_id": remediation_plan["id"]
            })
            
            return remediation_plan
        except Exception as e:
            self.logger.error(f"Remediation plan addition failed: {str(e)}")
            raise AuditError(f"Failed to add remediation plan: {str(e)}")
    
    def update_remediation_status(self, audit_id: str, remediation_id: str, status: str) -> Dict[str, Any]:
        """Update status of a remediation plan"""
        try:
            # Check if audit exists
            if audit_id not in self.audit_state["current_audits"]:
                raise AuditError(f"Audit {audit_id} not found")
            
            # Get audit
            audit = self.audit_state["current_audits"][audit_id]
            
            # Find the remediation plan
            remediation_plan = next((r for r in audit["remediation"] if r["id"] == remediation_id), None)
            if remediation_plan is None:
                raise AuditError(f"Remediation plan {remediation_id} not found in audit {audit_id}")
            
            # Validate status
            valid_statuses = ["OPEN", "IN_PROGRESS", "COMPLETED", "VERIFIED", "REJECTED"]
            if status not in valid_statuses:
                raise AuditError(f"Invalid status: {status}. Must be one of {valid_statuses}")
            
            # Update remediation plan status
            remediation_plan["status"] = status
            
            # If status is COMPLETED or VERIFIED, set completion date
            if status in ["COMPLETED", "VERIFIED"]:
                remediation_plan["completion_date"] = datetime.now().isoformat()
            
            # Update finding remediation status
            finding = next((f for f in audit["findings"] if f["id"] == remediation_plan["finding_id"]), None)
            if finding is not None:
                if status == "OPEN":
                    finding["remediation_status"] = "PLANNED"
                elif status == "IN_PROGRESS":
                    finding["remediation_status"] = "IN_PROGRESS"
                elif status == "COMPLETED":
                    finding["remediation_status"] = "COMPLETED"
                elif status == "VERIFIED":
                    finding["remediation_status"] = "VERIFIED"
                    finding["status"] = "CLOSED"
                elif status == "REJECTED":
                    finding["remediation_status"] = "REJECTED"
            
            # Log remediation status update
            self._log_audit_event(audit["standard"], "REMEDIATION_STATUS_UPDATED", {
                "audit_id": audit_id,
                "remediation_id": remediation_id,
                "finding_id": remediation_plan["finding_id"],
                "status": status
            })
            
            return remediation_plan
        except Exception as e:
            self.logger.error(f"Remediation status update failed: {str(e)}")
            raise AuditError(f"Failed to update remediation status: {str(e)}")
    
    def complete_audit(self, audit_id: str, summary: str = None) -> Dict[str, Any]:
        """Complete an audit"""
        try:
            # Check if audit exists
            if audit_id not in self.audit_state["current_audits"]:
                raise AuditError(f"Audit {audit_id} not found")
            
            # Get audit
            audit = self.audit_state["current_audits"][audit_id]
            
            # Check if audit is in correct state
            if audit["status"] != "IN_PROGRESS":
                raise AuditError(f"Audit {audit_id} is not in IN_PROGRESS state")
            
            # Update audit status
            audit["status"] = "COMPLETED"
            audit["completion_date"] = datetime.now().isoformat()
            audit["summary"] = summary
            
            # Calculate audit results
            total_findings = len(audit["findings"])
            open_findings = len([f for f in audit["findings"] if f["status"] == "OPEN"])
            closed_findings = len([f for f in audit["findings"] if f["status"] == "CLOSED"])
            high_severity_findings = len([f for f in audit["findings"] if f["severity"] == "high"])
            
            audit["results"] = {
                "total_findings": total_findings,
                "open_findings": open_findings,
                "closed_findings": closed_findings,
                "high_severity_findings": high_severity_findings,
                "compliance_percentage": 100 * (1 - open_findings / total_findings) if total_findings > 0 else 100
            }
            
            # Move audit to completed audits
            self.audit_state["completed_audits"][audit_id] = audit
            del self.audit_state["current_audits"][audit_id]
            
            # Add to audit history
            self.audit_state["audit_history"].append({
                "audit_id": audit_id,
                "standard": audit["standard"],
                "date": audit["completion_date"],
                "results": audit["results"]
            })
            
            # Update audit schedule
            self.audit_schedules[audit["standard"]]["last_audit"] = audit["completion_date"]
            self.audit_schedules[audit["standard"]]["next_audit"] = self._calculate_next_audit(audit["standard"])
            self.audit_schedules[audit["standard"]]["status"] = "SCHEDULED"
            
            # Update compliance state if audit results are good
            if audit["results"]["compliance_percentage"] >= 90:
                self.compliance_manager.compliance_state["standards"][audit["standard"]]["status"] = "COMPLIANT"
            else:
                self.compliance_manager.compliance_state["standards"][audit["standard"]]["status"] = "NON_COMPLIANT"
            
            # Log audit completion
            self._log_audit_event(audit["standard"], "AUDIT_COMPLETED", {
                "audit_id": audit_id,
                "completion_date": audit["completion_date"],
                "results": audit["results"]
            })
            
            # Store audit report
            self._store_audit_report(audit)
            
            return audit
        except Exception as e:
            self.logger.error(f"Audit completion failed: {str(e)}")
            raise AuditError(f"Failed to complete audit: {str(e)}")
    
    def _store_audit_report(self, audit: Dict[str, Any]) -> None:
        """Store audit report"""
        try:
            # Create reports directory if it doesn't exist
            reports_dir = Path("audit_reports")
            reports_dir.mkdir(exist_ok=True)
            
            # Create standard directory if it doesn't exist
            standard_dir = reports_dir / audit["standard"]
            standard_dir.mkdir(exist_ok=True)
            
            # Create report filename
            timestamp = datetime.fromisoformat(audit["completion_date"]).strftime("%Y%m%d_%H%M%S")
            filename = f"{audit['standard']}_audit_{timestamp}.json"
            
            # Store report
            with open(standard_dir / filename, "w") as f:
                json.dump(audit, f, indent=4)
        except Exception as e:
            self.logger.error(f"Audit report storage failed: {str(e)}")
            raise AuditError(f"Failed to store audit report: {str(e)}")
    
    def check_scheduled_audits(self) -> List[Dict[str, Any]]:
        """Check for audits that need to be scheduled"""
        try:
            audits_to_schedule = []
            now = datetime.now()
            
            for standard, schedule in self.audit_schedules.items():
                if schedule["status"] == "SCHEDULED":
                    next_audit = datetime.fromisoformat(schedule["next_audit"])
                    if next_audit <= now:
                        audits_to_schedule.append({
                            "standard": standard,
                            "scheduled_date": schedule["next_audit"]
                        })
            
            return audits_to_schedule
        except Exception as e:
            self.logger.error(f"Scheduled audits check failed: {str(e)}")
            raise AuditError(f"Failed to check scheduled audits: {str(e)}")
    
    def schedule_due_audits(self) -> List[str]:
        """Schedule all audits that are due"""
        try:
            scheduled_audits = []
            audits_to_schedule = self.check_scheduled_audits()
            
            for audit_info in audits_to_schedule:
                audit = self.schedule_audit(audit_info["standard"], audit_info["scheduled_date"])
                scheduled_audits.append(audit["id"])
            
            return scheduled_audits
        except Exception as e:
            self.logger.error(f"Scheduled audits scheduling failed: {str(e)}")
            raise AuditError(f"Failed to schedule due audits: {str(e)}")
    
    def get_open_findings(self, standard: str = None) -> List[Dict[str, Any]]:
        """Get all open findings, optionally filtered by standard"""
        try:
            all_findings = []
            
            if standard:
                # Validate standard
                self._validate_standard(standard)
                standards = [standard]
            else:
                standards = self.audit_findings.keys()
            
            for std in standards:
                for finding in self.audit_findings[std]:
                    if finding["status"] == "OPEN":
                        all_findings.append(finding)
            
            return all_findings
        except Exception as e:
            self.logger.error(f"Open findings retrieval failed: {str(e)}")
            raise AuditError(f"Failed to get open findings: {str(e)}")
    
    def get_open_remediations(self, standard: str = None) -> List[Dict[str, Any]]:
        """Get all open remediation plans, optionally filtered by standard"""
        try:
            all_remediations = []
            
            if standard:
                # Validate standard
                self._validate_standard(standard)
                standards = [standard]
            else:
                standards = self.audit_remediation.keys()
            
            for std in standards:
                for remediation in self.audit_remediation[std]:
                    if remediation["status"] in ["OPEN", "IN_PROGRESS"]:
                        all_remediations.append(remediation)
            
            return all_remediations
        except Exception as e:
            self.logger.error(f"Open remediations retrieval failed: {str(e)}")
            raise AuditError(f"Failed to get open remediations: {str(e)}")
    
    def get_audit_history(self, standard: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get audit history, optionally filtered by standard"""
        try:
            history = self.audit_state["audit_history"]
            
            if standard:
                # Validate standard
                self._validate_standard(standard)
                history = [h for h in history if h["standard"] == standard]
            
            # Sort by date (newest first) and limit
            history = sorted(history, key=lambda x: x["date"], reverse=True)[:limit]
            
            return history
        except Exception as e:
            self.logger.error(f"Audit history retrieval failed: {str(e)}")
            raise AuditError(f"Failed to get audit history: {str(e)}")
    
    def _log_audit_event(self, standard: str, event_type: str, data: Dict[str, Any]) -> None:
        """Log audit event to audit trail"""
        try:
            self.audit_trail.log_event(
                event_type,
                {
                    "standard": standard,
                    "timestamp": datetime.now().isoformat(),
                    **data
                }
            )
        except Exception as e:
            self.logger.error(f"Audit event logging failed: {str(e)}")
            # Don't raise an exception here to prevent disruption of audit operations
