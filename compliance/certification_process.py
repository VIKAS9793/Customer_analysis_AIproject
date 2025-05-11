from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import hashlib
import uuid
from security.audit_trail import AuditTrail
from security.hsm import HSM
from compliance.compliance_config import COMPLIANCE_CONFIG
from compliance.compliance_manager import ComplianceManager

class CertificationError(Exception):
    """Raised when certification operations fail"""
    pass

class CertificationProcess:
    """Handles compliance certification processes and evidence management"""
    
    def __init__(self, config: Dict[str, Any], compliance_manager: ComplianceManager):
        """Initialize certification process with secure configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.compliance_manager = compliance_manager
        
        # Initialize security components
        self.hsm = HSM(config)
        self.audit = AuditTrail(config)
        
        # Initialize certification state
        self.certification_state = self._initialize_certification_state()
        
        # Initialize evidence store
        self.evidence_store = self._initialize_evidence_store()
        
        # Initialize certification workflows
        self.workflows = self._initialize_workflows()
        
        # Initialize certification templates
        self.templates = self._initialize_templates()
    
    def _initialize_certification_state(self) -> Dict[str, Any]:
        """Initialize certification state tracking"""
        try:
            return {
                "certifications": self._initialize_certifications(),
                "current_cycle": self._get_current_certification_cycle(),
                "status": "ACTIVE",
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Certification state initialization failed: {str(e)}")
            raise CertificationError(f"Failed to initialize certification state: {str(e)}")
    
    def _initialize_certifications(self) -> Dict[str, Dict[str, Any]]:
        """Initialize certifications for each standard"""
        try:
            certifications = {}
            for standard, config in COMPLIANCE_CONFIG["standards"].items():
                if config["enabled"]:
                    certifications[standard] = {
                        "version": config["version"],
                        "status": "PENDING",
                        "last_certification": None,
                        "expiration": None,
                        "evidence": [],
                        "approvals": [],
                        "certificate_id": None
                    }
            return certifications
        except Exception as e:
            self.logger.error(f"Certifications initialization failed: {str(e)}")
            raise CertificationError(f"Failed to initialize certifications: {str(e)}")
    
    def _get_current_certification_cycle(self) -> Dict[str, Any]:
        """Get current certification cycle information"""
        try:
            now = datetime.now()
            year = now.year
            quarter = (now.month - 1) // 3 + 1
            
            return {
                "year": year,
                "quarter": quarter,
                "start_date": datetime(year, (quarter - 1) * 3 + 1, 1).isoformat(),
                "end_date": datetime(year if quarter < 4 else year + 1, 
                                    ((quarter) % 4 + 1) * 3 if quarter < 4 else 1, 
                                    1).isoformat(),
                "status": "IN_PROGRESS"
            }
        except Exception as e:
            self.logger.error(f"Certification cycle initialization failed: {str(e)}")
            raise CertificationError(f"Failed to initialize certification cycle: {str(e)}")
    
    def _initialize_evidence_store(self) -> Dict[str, Any]:
        """Initialize evidence store"""
        try:
            # Create evidence directory if it doesn't exist
            evidence_dir = Path("evidence")
            evidence_dir.mkdir(exist_ok=True)
            
            return {
                "base_path": evidence_dir,
                "evidence_items": {},
                "retention_period": "7y",
                "encryption": True,
                "integrity_check": True
            }
        except Exception as e:
            self.logger.error(f"Evidence store initialization failed: {str(e)}")
            raise CertificationError(f"Failed to initialize evidence store: {str(e)}")
    
    def _initialize_workflows(self) -> Dict[str, Dict[str, Any]]:
        """Initialize certification workflows"""
        try:
            return {
                "pci_dss": {
                    "steps": [
                        {"name": "gap_assessment", "status": "PENDING", "required": True},
                        {"name": "evidence_collection", "status": "PENDING", "required": True},
                        {"name": "internal_audit", "status": "PENDING", "required": True},
                        {"name": "remediation", "status": "PENDING", "required": True},
                        {"name": "external_audit", "status": "PENDING", "required": True},
                        {"name": "certification_issuance", "status": "PENDING", "required": True}
                    ],
                    "current_step": "gap_assessment",
                    "approvers": ["compliance_officer", "security_officer", "ciso"]
                },
                "iso_27001": {
                    "steps": [
                        {"name": "scope_definition", "status": "PENDING", "required": True},
                        {"name": "risk_assessment", "status": "PENDING", "required": True},
                        {"name": "controls_implementation", "status": "PENDING", "required": True},
                        {"name": "internal_audit", "status": "PENDING", "required": True},
                        {"name": "management_review", "status": "PENDING", "required": True},
                        {"name": "external_audit", "status": "PENDING", "required": True},
                        {"name": "certification_issuance", "status": "PENDING", "required": True}
                    ],
                    "current_step": "scope_definition",
                    "approvers": ["compliance_officer", "security_officer", "ciso"]
                },
                "hipaa": {
                    "steps": [
                        {"name": "gap_assessment", "status": "PENDING", "required": True},
                        {"name": "risk_analysis", "status": "PENDING", "required": True},
                        {"name": "controls_implementation", "status": "PENDING", "required": True},
                        {"name": "policy_development", "status": "PENDING", "required": True},
                        {"name": "training", "status": "PENDING", "required": True},
                        {"name": "assessment", "status": "PENDING", "required": True},
                        {"name": "attestation", "status": "PENDING", "required": True}
                    ],
                    "current_step": "gap_assessment",
                    "approvers": ["compliance_officer", "privacy_officer", "security_officer"]
                }
            }
        except Exception as e:
            self.logger.error(f"Workflows initialization failed: {str(e)}")
            raise CertificationError(f"Failed to initialize workflows: {str(e)}")
    
    def _initialize_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize certification templates"""
        try:
            return {
                "pci_dss": {
                    "title": "Payment Card Industry Data Security Standard (PCI DSS) Certification",
                    "version": COMPLIANCE_CONFIG["standards"]["pci_dss"]["version"],
                    "sections": [
                        {"name": "scope", "title": "Certification Scope", "required": True},
                        {"name": "methodology", "title": "Assessment Methodology", "required": True},
                        {"name": "findings", "title": "Assessment Findings", "required": True},
                        {"name": "attestation", "title": "Attestation of Compliance", "required": True},
                        {"name": "evidence", "title": "Evidence Summary", "required": True}
                    ],
                    "metadata": {
                        "issuer": "PCI Security Standards Council",
                        "validity_period": "1y"
                    }
                },
                "iso_27001": {
                    "title": "ISO/IEC 27001 Information Security Management System Certification",
                    "version": COMPLIANCE_CONFIG["standards"]["iso_27001"]["version"],
                    "sections": [
                        {"name": "scope", "title": "Certification Scope", "required": True},
                        {"name": "statement", "title": "Statement of Applicability", "required": True},
                        {"name": "assessment", "title": "Assessment Results", "required": True},
                        {"name": "nonconformities", "title": "Nonconformities", "required": True},
                        {"name": "certification", "title": "Certification Statement", "required": True}
                    ],
                    "metadata": {
                        "issuer": "Accredited Certification Body",
                        "validity_period": "3y"
                    }
                },
                "hipaa": {
                    "title": "HIPAA Compliance Attestation",
                    "version": COMPLIANCE_CONFIG["standards"]["hipaa"]["version"],
                    "sections": [
                        {"name": "scope", "title": "Attestation Scope", "required": True},
                        {"name": "assessment", "title": "Security Rule Assessment", "required": True},
                        {"name": "privacy", "title": "Privacy Rule Assessment", "required": True},
                        {"name": "breachnotification", "title": "Breach Notification Assessment", "required": True},
                        {"name": "attestation", "title": "Attestation Statement", "required": True}
                    ],
                    "metadata": {
                        "issuer": "Organization",
                        "validity_period": "1y"
                    }
                }
            }
        except Exception as e:
            self.logger.error(f"Templates initialization failed: {str(e)}")
            raise CertificationError(f"Failed to initialize templates: {str(e)}")
    
    def start_certification_process(self, standard: str) -> Dict[str, Any]:
        """Start certification process for a specific standard"""
        try:
            # Validate standard
            if standard not in COMPLIANCE_CONFIG["standards"]:
                raise CertificationError(f"Unsupported standard: {standard}")
            
            # Check if standard is enabled
            if not COMPLIANCE_CONFIG["standards"][standard]["enabled"]:
                raise CertificationError(f"Standard {standard} is not enabled")
            
            # Check if certification is already in progress
            if self.certification_state["certifications"][standard]["status"] == "IN_PROGRESS":
                raise CertificationError(f"Certification for {standard} is already in progress")
            
            # Initialize certification
            self.certification_state["certifications"][standard] = {
                "version": COMPLIANCE_CONFIG["standards"][standard]["version"],
                "status": "IN_PROGRESS",
                "start_date": datetime.now().isoformat(),
                "last_certification": None,
                "expiration": None,
                "evidence": [],
                "approvals": [],
                "certificate_id": None
            }
            
            # Reset workflow steps
            self._reset_workflow_steps(standard)
            
            # Log certification start
            self._log_certification_event(standard, "CERTIFICATION_STARTED", {
                "version": COMPLIANCE_CONFIG["standards"][standard]["version"],
                "cycle": self.certification_state["current_cycle"]
            })
            
            return self.certification_state["certifications"][standard]
        except Exception as e:
            self.logger.error(f"Certification process start failed: {str(e)}")
            raise CertificationError(f"Failed to start certification process: {str(e)}")
    
    def _reset_workflow_steps(self, standard: str) -> None:
        """Reset workflow steps for a standard"""
        try:
            for step in self.workflows[standard]["steps"]:
                step["status"] = "PENDING"
            
            self.workflows[standard]["current_step"] = self.workflows[standard]["steps"][0]["name"]
        except Exception as e:
            self.logger.error(f"Workflow reset failed: {str(e)}")
            raise CertificationError(f"Failed to reset workflow: {str(e)}")
    
    def advance_certification_step(self, standard: str) -> Dict[str, Any]:
        """Advance to the next step in the certification process"""
        try:
            # Validate standard
            if standard not in COMPLIANCE_CONFIG["standards"]:
                raise CertificationError(f"Unsupported standard: {standard}")
            
            # Check if certification is in progress
            if self.certification_state["certifications"][standard]["status"] != "IN_PROGRESS":
                raise CertificationError(f"Certification for {standard} is not in progress")
            
            # Get current step
            current_step_name = self.workflows[standard]["current_step"]
            current_step_index = next(
                (i for i, step in enumerate(self.workflows[standard]["steps"]) 
                 if step["name"] == current_step_name),
                None
            )
            
            if current_step_index is None:
                raise CertificationError(f"Current step {current_step_name} not found in workflow")
            
            # Mark current step as completed
            self.workflows[standard]["steps"][current_step_index]["status"] = "COMPLETED"
            
            # Check if this was the last step
            if current_step_index == len(self.workflows[standard]["steps"]) - 1:
                # Certification process is complete
                self._complete_certification(standard)
                return self.certification_state["certifications"][standard]
            
            # Advance to next step
            next_step_index = current_step_index + 1
            next_step_name = self.workflows[standard]["steps"][next_step_index]["name"]
            self.workflows[standard]["current_step"] = next_step_name
            
            # Log step advancement
            self._log_certification_event(standard, "CERTIFICATION_STEP_ADVANCED", {
                "previous_step": current_step_name,
                "current_step": next_step_name
            })
            
            return {
                "standard": standard,
                "previous_step": current_step_name,
                "current_step": next_step_name,
                "steps_completed": current_step_index + 1,
                "total_steps": len(self.workflows[standard]["steps"])
            }
        except Exception as e:
            self.logger.error(f"Certification step advancement failed: {str(e)}")
            raise CertificationError(f"Failed to advance certification step: {str(e)}")
    
    def _complete_certification(self, standard: str) -> None:
        """Complete certification process for a standard"""
        try:
            # Generate certificate ID
            certificate_id = self._generate_certificate_id(standard)
            
            # Calculate expiration date based on validity period
            validity_period = self.templates[standard]["metadata"]["validity_period"]
            validity_years = int(validity_period[:-1])
            expiration_date = datetime.now() + timedelta(days=365 * validity_years)
            
            # Update certification state
            self.certification_state["certifications"][standard].update({
                "status": "CERTIFIED",
                "completion_date": datetime.now().isoformat(),
                "last_certification": datetime.now().isoformat(),
                "expiration": expiration_date.isoformat(),
                "certificate_id": certificate_id
            })
            
            # Generate certificate
            certificate = self._generate_certificate(standard, certificate_id, expiration_date)
            
            # Store certificate
            self._store_certificate(standard, certificate_id, certificate)
            
            # Log certification completion
            self._log_certification_event(standard, "CERTIFICATION_COMPLETED", {
                "certificate_id": certificate_id,
                "expiration": expiration_date.isoformat()
            })
        except Exception as e:
            self.logger.error(f"Certification completion failed: {str(e)}")
            raise CertificationError(f"Failed to complete certification: {str(e)}")
    
    def _generate_certificate_id(self, standard: str) -> str:
        """Generate unique certificate ID"""
        try:
            # Create a unique ID based on standard, version, and timestamp
            unique_string = f"{standard}_{COMPLIANCE_CONFIG['standards'][standard]['version']}_{datetime.now().isoformat()}"
            
            # Generate UUID based on the unique string
            namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # Namespace for URLs
            certificate_id = str(uuid.uuid5(namespace, unique_string))
            
            return certificate_id
        except Exception as e:
            self.logger.error(f"Certificate ID generation failed: {str(e)}")
            raise CertificationError(f"Failed to generate certificate ID: {str(e)}")
    
    def _generate_certificate(self, standard: str, certificate_id: str, expiration_date: datetime) -> Dict[str, Any]:
        """Generate certificate for a standard"""
        try:
            template = self.templates[standard]
            
            certificate = {
                "certificate_id": certificate_id,
                "title": template["title"],
                "standard": standard,
                "version": template["version"],
                "organization": self.config.get("organization", "FinConnectAI"),
                "issue_date": datetime.now().isoformat(),
                "expiration_date": expiration_date.isoformat(),
                "issuer": template["metadata"]["issuer"],
                "scope": self._get_certification_scope(standard),
                "attestation": self._get_attestation_statement(standard),
                "approvals": self.certification_state["certifications"][standard]["approvals"],
                "digital_signature": None  # Will be added by _store_certificate
            }
            
            return certificate
        except Exception as e:
            self.logger.error(f"Certificate generation failed: {str(e)}")
            raise CertificationError(f"Failed to generate certificate: {str(e)}")
    
    def _get_certification_scope(self, standard: str) -> Dict[str, Any]:
        """Get certification scope for a standard"""
        try:
            # This would typically be defined during the certification process
            # For now, return a default scope
            return {
                "systems": [
                    "authentication",
                    "authorization",
                    "encryption",
                    "api_security",
                    "network_security"
                ],
                "data_types": [
                    "customer_data",
                    "transaction_data",
                    "authentication_data"
                ],
                "locations": [
                    "primary_datacenter",
                    "backup_datacenter"
                ],
                "exclusions": []
            }
        except Exception as e:
            self.logger.error(f"Certification scope retrieval failed: {str(e)}")
            raise CertificationError(f"Failed to get certification scope: {str(e)}")
    
    def _get_attestation_statement(self, standard: str) -> str:
        """Get attestation statement for a standard"""
        try:
            organization = self.config.get("organization", "FinConnectAI")
            version = COMPLIANCE_CONFIG["standards"][standard]["version"]
            
            if standard == "pci_dss":
                return f"{organization} has been assessed and found to be in compliance with Payment Card Industry Data Security Standard (PCI DSS) version {version} as of {datetime.now().strftime('%Y-%m-%d')}."
            elif standard == "iso_27001":
                return f"{organization} has been assessed and found to be in compliance with ISO/IEC 27001:{version} Information Security Management System standard as of {datetime.now().strftime('%Y-%m-%d')}."
            elif standard == "hipaa":
                return f"{organization} has been assessed and found to be in compliance with Health Insurance Portability and Accountability Act (HIPAA) Security, Privacy, and Breach Notification Rules as of {datetime.now().strftime('%Y-%m-%d')}."
            else:
                return f"{organization} has been assessed and found to be in compliance with {standard} version {version} as of {datetime.now().strftime('%Y-%m-%d')}."
        except Exception as e:
            self.logger.error(f"Attestation statement generation failed: {str(e)}")
            raise CertificationError(f"Failed to generate attestation statement: {str(e)}")
    
    def _store_certificate(self, standard: str, certificate_id: str, certificate: Dict[str, Any]) -> None:
        """Store certificate and sign it"""
        try:
            # Create certificates directory if it doesn't exist
            certificates_dir = Path("certificates")
            certificates_dir.mkdir(exist_ok=True)
            
            # Create standard directory if it doesn't exist
            standard_dir = certificates_dir / standard
            standard_dir.mkdir(exist_ok=True)
            
            # Sign certificate
            certificate_json = json.dumps(certificate, indent=4)
            signature = self.hsm.sign_data(certificate_json.encode())
            certificate["digital_signature"] = signature
            
            # Store certificate
            certificate_path = standard_dir / f"{certificate_id}.json"
            with open(certificate_path, "w") as f:
                json.dump(certificate, f, indent=4)
        except Exception as e:
            self.logger.error(f"Certificate storage failed: {str(e)}")
            raise CertificationError(f"Failed to store certificate: {str(e)}")
    
    def add_evidence(self, standard: str, evidence_type: str, evidence_data: Dict[str, Any]) -> str:
        """Add evidence for a certification"""
        try:
            # Validate standard
            if standard not in COMPLIANCE_CONFIG["standards"]:
                raise CertificationError(f"Unsupported standard: {standard}")
            
            # Check if certification is in progress
            if self.certification_state["certifications"][standard]["status"] != "IN_PROGRESS":
                raise CertificationError(f"Certification for {standard} is not in progress")
            
            # Generate evidence ID
            evidence_id = self._generate_evidence_id(standard, evidence_type)
            
            # Prepare evidence
            evidence = {
                "id": evidence_id,
                "standard": standard,
                "type": evidence_type,
                "data": evidence_data,
                "timestamp": datetime.now().isoformat(),
                "hash": None  # Will be added by _store_evidence
            }
            
            # Store evidence
            self._store_evidence(standard, evidence_id, evidence)
            
            # Add evidence to certification
            self.certification_state["certifications"][standard]["evidence"].append(evidence_id)
            
            # Log evidence addition
            self._log_certification_event(standard, "EVIDENCE_ADDED", {
                "evidence_id": evidence_id,
                "evidence_type": evidence_type
            })
            
            return evidence_id
        except Exception as e:
            self.logger.error(f"Evidence addition failed: {str(e)}")
            raise CertificationError(f"Failed to add evidence: {str(e)}")
    
    def _generate_evidence_id(self, standard: str, evidence_type: str) -> str:
        """Generate unique evidence ID"""
        try:
            # Create a unique ID based on standard, evidence type, and timestamp
            unique_string = f"{standard}_{evidence_type}_{datetime.now().isoformat()}"
            
            # Generate UUID based on the unique string
            namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # Namespace for URLs
            evidence_id = str(uuid.uuid5(namespace, unique_string))
            
            return evidence_id
        except Exception as e:
            self.logger.error(f"Evidence ID generation failed: {str(e)}")
            raise CertificationError(f"Failed to generate evidence ID: {str(e)}")
    
    def _store_evidence(self, standard: str, evidence_id: str, evidence: Dict[str, Any]) -> None:
        """Store evidence and calculate hash"""
        try:
            # Create evidence directory if it doesn't exist
            evidence_dir = self.evidence_store["base_path"]
            
            # Create standard directory if it doesn't exist
            standard_dir = evidence_dir / standard
            standard_dir.mkdir(exist_ok=True)
            
            # Calculate evidence hash
            evidence_json = json.dumps(evidence["data"], sort_keys=True)
            evidence_hash = hashlib.sha256(evidence_json.encode()).hexdigest()
            evidence["hash"] = evidence_hash
            
            # Store evidence
            evidence_path = standard_dir / f"{evidence_id}.json"
            with open(evidence_path, "w") as f:
                json.dump(evidence, f, indent=4)
            
            # Add to evidence store
            self.evidence_store["evidence_items"][evidence_id] = {
                "path": str(evidence_path),
                "hash": evidence_hash,
                "timestamp": evidence["timestamp"]
            }
        except Exception as e:
            self.logger.error(f"Evidence storage failed: {str(e)}")
            raise CertificationError(f"Failed to store evidence: {str(e)}")
    
    def get_evidence(self, evidence_id: str) -> Dict[str, Any]:
        """Get evidence by ID"""
        try:
            # Check if evidence exists
            if evidence_id not in self.evidence_store["evidence_items"]:
                raise CertificationError(f"Evidence {evidence_id} not found")
            
            # Get evidence path
            evidence_path = self.evidence_store["evidence_items"][evidence_id]["path"]
            
            # Read evidence
            with open(evidence_path, "r") as f:
                evidence = json.load(f)
            
            # Verify evidence integrity
            evidence_json = json.dumps(evidence["data"], sort_keys=True)
            calculated_hash = hashlib.sha256(evidence_json.encode()).hexdigest()
            
            if calculated_hash != evidence["hash"]:
                raise CertificationError(f"Evidence {evidence_id} integrity check failed")
            
            return evidence
        except Exception as e:
            self.logger.error(f"Evidence retrieval failed: {str(e)}")
            raise CertificationError(f"Failed to get evidence: {str(e)}")
    
    def add_approval(self, standard: str, approver: str, comments: str = None) -> Dict[str, Any]:
        """Add approval for a certification"""
        try:
            # Validate standard
            if standard not in COMPLIANCE_CONFIG["standards"]:
                raise CertificationError(f"Unsupported standard: {standard}")
            
            # Check if certification is in progress
            if self.certification_state["certifications"][standard]["status"] != "IN_PROGRESS":
                raise CertificationError(f"Certification for {standard} is not in progress")
            
            # Check if approver is authorized
            if approver not in self.workflows[standard]["approvers"]:
                raise CertificationError(f"Approver {approver} is not authorized for {standard}")
            
            # Check if approver has already approved
            for approval in self.certification_state["certifications"][standard]["approvals"]:
                if approval["approver"] == approver:
                    raise CertificationError(f"Approver {approver} has already approved")
            
            # Add approval
            approval = {
                "approver": approver,
                "timestamp": datetime.now().isoformat(),
                "comments": comments
            }
            
            self.certification_state["certifications"][standard]["approvals"].append(approval)
            
            # Log approval
            self._log_certification_event(standard, "APPROVAL_ADDED", {
                "approver": approver,
                "timestamp": approval["timestamp"]
            })
            
            return approval
        except Exception as e:
            self.logger.error(f"Approval addition failed: {str(e)}")
            raise CertificationError(f"Failed to add approval: {str(e)}")
    
    def verify_certificate(self, certificate_id: str) -> Dict[str, Any]:
        """Verify certificate by ID"""
        try:
            # Find certificate
            certificates_dir = Path("certificates")
            
            # Search for certificate in all standard directories
            certificate_path = None
            for standard_dir in certificates_dir.iterdir():
                if standard_dir.is_dir():
                    potential_path = standard_dir / f"{certificate_id}.json"
                    if potential_path.exists():
                        certificate_path = potential_path
                        break
            
            if certificate_path is None:
                raise CertificationError(f"Certificate {certificate_id} not found")
            
            # Read certificate
            with open(certificate_path, "r") as f:
                certificate = json.load(f)
            
            # Verify signature
            certificate_copy = certificate.copy()
            signature = certificate_copy.pop("digital_signature")
            certificate_json = json.dumps(certificate_copy, indent=4)
            
            if not self.hsm.verify_signature(certificate_json.encode(), signature):
                raise CertificationError(f"Certificate {certificate_id} signature verification failed")
            
            return {
                "certificate_id": certificate_id,
                "verification_status": "VALID",
                "verification_timestamp": datetime.now().isoformat(),
                "certificate": certificate
            }
        except Exception as e:
            self.logger.error(f"Certificate verification failed: {str(e)}")
            raise CertificationError(f"Failed to verify certificate: {str(e)}")
    
    def check_certification_status(self, standard: str) -> Dict[str, Any]:
        """Check certification status for a standard"""
        try:
            # Validate standard
            if standard not in COMPLIANCE_CONFIG["standards"]:
                raise CertificationError(f"Unsupported standard: {standard}")
            
            # Get certification state
            certification = self.certification_state["certifications"][standard]
            
            # Check if certified
            if certification["status"] == "CERTIFIED":
                # Check if expired
                expiration = datetime.fromisoformat(certification["expiration"])
                if expiration < datetime.now():
                    status = "EXPIRED"
                else:
                    status = "VALID"
            else:
                status = certification["status"]
            
            return {
                "standard": standard,
                "status": status,
                "certification": certification,
                "workflow": self.workflows[standard] if certification["status"] == "IN_PROGRESS" else None
            }
        except Exception as e:
            self.logger.error(f"Certification status check failed: {str(e)}")
            raise CertificationError(f"Failed to check certification status: {str(e)}")
    
    def _log_certification_event(self, standard: str, event_type: str, data: Dict[str, Any]) -> None:
        """Log certification event"""
        try:
            self.audit.log_event(
                event_type,
                {
                    "standard": standard,
                    "timestamp": datetime.now().isoformat(),
                    **data
                }
            )
        except Exception as e:
            self.logger.error(f"Certification event logging failed: {str(e)}")
            # Don't raise an exception here, as the certification operation was successful
