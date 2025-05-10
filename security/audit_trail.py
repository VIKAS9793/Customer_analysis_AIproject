"""
Audit Trail System

This module implements enterprise-grade audit trail logging following NIST SP 800-53 and ISO 27001 standards.
"""

from typing import Dict, Any, Optional, List
import logging
import json
from datetime import datetime, timedelta
import os
import hashlib
import hmac
from security.hsm import HSM

class AuditTrailError(Exception):
    """Raised when audit trail operations fail"""
    pass

class AuditTrail:
    """
    Enterprise-grade audit trail system.
    
    Implements NIST SP 800-53 AU-1 through AU-14 controls.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize audit trail system.
        
        Args:
            config: Configuration containing:
                - log_retention_days: Number of days to retain logs
                - log_rotation_days: Number of days before rotating logs
                - audit_frequency: Frequency of audit checks
                - hsm_config: HSM configuration for log signing
                - encryption_key: Key for log encryption
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Audit configuration
        self.log_retention_days = config.get("log_retention_days", 365)
        self.log_rotation_days = config.get("log_rotation_days", 7)
        self.audit_frequency = config.get("audit_frequency", "daily")
        
        # Security configuration
        self.hsm = HSM(config["hsm_config"])
        self.encryption_key = config["encryption_key"]
        self.signing_key = config["signing_key"]
        
        # Create audit directories
        self.log_dir = "logs/audit"
        self.archive_dir = "logs/audit_archive"
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.archive_dir, exist_ok=True)
        
        # Initialize audit state
        self.current_log_file = self._get_log_file()
        self.last_rotation = datetime.now()
        self.last_cleanup = datetime.now()
        
    def _get_log_file(self) -> str:
        """Get current audit log file name"""
        date_str = datetime.now().strftime("%Y%m%d")
        return os.path.join(self.log_dir, f"audit_{date_str}.jsonl")
    
    def _sign_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Sign audit record using HSM"""
        record_str = json.dumps(record, sort_keys=True)
        signature = self.hsm.sign(self.signing_key, record_str.encode())
        return {
            **record,
            "signature": signature.hex(),
            "signature_algorithm": "RSA-PSS"
        }
    
    def _encrypt_record(self, record: Dict[str, Any]) -> str:
        """Encrypt audit record"""
        record_str = json.dumps(record, sort_keys=True)
        encrypted = self.hsm.encrypt(self.encryption_key, record_str.encode())
        return encrypted.hex()
    
    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Log an audit event with proper security controls.
        
        Args:
            event_type: Type of event (e.g., authentication, access)
            data: Event data including user_id, session_id, etc.
            
        Raises:
            AuditTrailError: If logging fails
        """
        try:
            # Create audit record
            audit_record = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "data": data,
                "user_id": data.get("user_id", "SYSTEM"),
                "session_id": data.get("session_id", "-"),
                "ip_address": data.get("ip_address", "-"),
                "action": data.get("action", "-"),
                "status": data.get("status", "-"),
                "details": data.get("details", {}),
                "risk_level": data.get("risk_level", "low"),
                "category": data.get("category", "general")
            }
            
            # Sign and encrypt record
            signed_record = self._sign_record(audit_record)
            encrypted_record = self._encrypt_record(signed_record)
            
            # Write to log file
            with open(self.current_log_file, "a") as f:
                f.write(encrypted_record + "\n")
            
            # Check for log rotation
            if (datetime.now() - self.last_rotation) > timedelta(days=self.log_rotation_days):
                self._rotate_logs()
            
            # Check for cleanup
            if (datetime.now() - self.last_cleanup) > timedelta(days=1):
                self._cleanup_old_logs()
            
        except Exception as e:
            self.logger.error(f"Failed to log audit event: {str(e)}")
            raise AuditTrailError(f"Failed to log audit event: {str(e)}")
    
    def _rotate_logs(self) -> None:
        """Rotate audit logs"""
        try:
            current_time = datetime.now()
            date_str = current_time.strftime("%Y%m%d_%H%M%S")
            
            # Create archive filename
            archive_file = os.path.join(
                self.archive_dir,
                f"audit_archive_{date_str}.jsonl"
            )
            
            # Move current log to archive
            os.rename(self.current_log_file, archive_file)
            
            # Create new log file
            self.current_log_file = self._get_log_file()
            
            self.last_rotation = current_time
            self.logger.info(f"Audit logs rotated successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to rotate audit logs: {str(e)}")
            raise AuditTrailError(f"Failed to rotate audit logs: {str(e)}")
    
    def _cleanup_old_logs(self) -> None:
        """Clean up old audit logs"""
        try:
            current_time = datetime.now()
            retention_period = timedelta(days=self.log_retention_days)
            
            # Clean up archived logs
            for filename in os.listdir(self.archive_dir):
                if filename.endswith(".jsonl"):
                    file_path = os.path.join(self.archive_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if current_time - file_time > retention_period:
                        os.remove(file_path)
                        self.logger.info(f"Removed old audit log: {filename}")
            
            self.last_cleanup = current_time
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old logs: {str(e)}")
            raise AuditTrailError(f"Failed to cleanup old logs: {str(e)}")
    
    def get_audit_trail(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Get audit trail for a date range.
        
        Args:
            start_date: Start date for audit trail
            end_date: End date for audit trail
            
        Returns:
            List of decrypted and verified audit records
            
        Raises:
            AuditTrailError: If audit trail retrieval fails
        """
        try:
            audit_records = []
            
            # Get all relevant log files
            log_files = []
            for filename in os.listdir(self.log_dir):
                if filename.endswith(".jsonl"):
                    file_date = datetime.strptime(filename[6:14], "%Y%m%d")
                    if start_date <= file_date <= end_date:
                        log_files.append(os.path.join(self.log_dir, filename))
            
            # Process each log file
            for log_file in log_files:
                with open(log_file, "r") as f:
                    for line in f:
                        try:
                            # Decrypt record
                            encrypted_record = line.strip()
                            record_str = self.hsm.decrypt(self.encryption_key, bytes.fromhex(encrypted_record))
                            record = json.loads(record_str)
                            
                            # Verify signature
                            record_str = json.dumps({k: v for k, v in record.items() if k != "signature"}, sort_keys=True)
                            if not self.hsm.verify(self.signing_key, record_str.encode(), bytes.fromhex(record["signature"])):
                                self.logger.warning(f"Invalid signature in audit log: {record["timestamp"]}")
                                continue
                            
                            audit_records.append(record)
                            
                        except Exception as e:
                            self.logger.error(f"Failed to process audit record: {str(e)}")
                            continue
            
            return audit_records
            
        except Exception as e:
            self.logger.error(f"Failed to get audit trail: {str(e)}")
            raise AuditTrailError(f"Failed to get audit trail: {str(e)}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get audit trail system metrics"""
        metrics = {
            "active_log_file": self.current_log_file,
            "last_rotation": self.last_rotation.isoformat(),
            "last_cleanup": self.last_cleanup.isoformat(),
            "log_retention_days": self.log_retention_days,
            "log_rotation_days": self.log_rotation_days,
            "log_size": os.path.getsize(self.current_log_file) if os.path.exists(self.current_log_file) else 0,
            "total_logs": len(os.listdir(self.log_dir)) + len(os.listdir(self.archive_dir))
        }
        return metrics

    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Log security event with proper controls

        Args:
            event_type: Type of security event
            data: Event data to log
        """
        try:
            audit_record = {
                "event_type": event_type,
                "timestamp": datetime.datetime.now().isoformat(),
                "data": data,
                "user_id": data.get("user_id", "SYSTEM"),
                "risk_level": data.get("risk_level", "low"),
                "category": data.get("category", "general")
            }

            # Sign and encrypt the audit record
            signature = self.hsm.sign(
                self.config["audit_key_id"],
                json.dumps(audit_record).encode()
            )
            
            # Create HSM-encrypted record
            encrypted_record = self.hsm.encrypt(
                self.config["audit_key_id"],
                json.dumps({
                    "record": audit_record,
                    "signature": base64.b64encode(signature).decode()
                }).encode()
            )

            # Write to audit log
            with open(self.config["audit_log_path"], "ab") as f:
                f.write(encrypted_record + b"\n")

            self.logger.info(f"Audit event logged: {event_type}")
        except Exception as e:
            self.logger.error(f"Audit logging failed: {str(e)}")
            raise AuditTrailError(f"Failed to log audit event: {str(e)}")

    def log_access(self, user_id: str, resource: str, action: str) -> None:
        """Log access event"""
        self.log_event(
            "ACCESS",
            {
                "user_id": user_id,
                "resource": resource,
                "action": action,
                "status": "SUCCESS"
            }
        )
    
    def log_transaction(self, transaction_id: str, status: str, details: Dict[str, Any]) -> None:
        """Log transaction event"""
        self.log_event(
            "TRANSACTION",
            {
                "transaction_id": transaction_id,
                "status": status,
                "details": details
            }
        )
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log security event"""
        self.log_event(
            "SECURITY",
            {
                "event_type": event_type,
                "details": details
            }
        )
    
    def get_audit_logs(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get audit logs for a date range"""
        try:
            logs = []
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
            
            current_date = start
            while current_date <= end:
                date_str = current_date.strftime("%Y%m%d")
                log_file = os.path.join(self.log_dir, f"audit_{date_str}.jsonl")
                
                if os.path.exists(log_file):
                    with open(log_file, "r") as f:
                        for line in f:
                            log = json.loads(line)
                            logs.append(log)
                
                current_date += timedelta(days=1)
            
            return logs
        except Exception as e:
            self.logger.error(f"Failed to get audit logs: {str(e)}")
            raise AuditTrailError(f"Failed to retrieve audit logs: {str(e)}")
    
    def rotate_logs(self) -> None:
        """Rotate audit logs according to policy"""
        try:
            current_date = datetime.now()
            retention_date = current_date - timedelta(days=self.log_retention_days)
            
            for file in os.listdir(self.log_dir):
                if file.startswith("audit_"):
                    file_date_str = file[6:14]
                    file_date = datetime.strptime(file_date_str, "%Y%m%d")
                    
                    if file_date < retention_date:
                        os.remove(os.path.join(self.log_dir, file))
                        self.logger.info(f"Removed old audit log: {file}")
        except Exception as e:
            self.logger.error(f"Log rotation failed: {str(e)}")
            raise AuditTrailError(f"Failed to rotate audit logs: {str(e)}")
