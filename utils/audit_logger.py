import logging
from datetime import datetime
import os
from pathlib import Path

class AuditLogger:
    def __init__(self, log_path: str = "audit.log"):
        """Initialize audit logger.
        
        Args:
            log_path: Path to audit log file
        """
        self.log_path = log_path
        self._setup_logger()

    def _setup_logger(self):
        """Setup audit logger configuration."""
        # Create logs directory if it doesn't exist
        log_dir = Path(self.log_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        # Configure logger
        logging.basicConfig(
            filename=self.log_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def log_event(self, event_type: str, details: dict):
        """Log an audit event.
        
        Args:
            event_type: Type of event (e.g., FRAUD_DETECTION, KYC_VERIFICATION)
            details: Dictionary containing event details
        """
        log_message = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        }
        logging.info(f"Audit Event: {log_message}")

    def log_fraud_detection(self, transaction_id: str, decision: str, confidence: float):
        """Log fraud detection event.
        
        Args:
            transaction_id: ID of the transaction
            decision: Decision made (APPROVE/REJECT/FLAG)
            confidence: Confidence score
        """
        self.log_event(
            "FRAUD_DETECTION",
            {
                "transaction_id": transaction_id,
                "decision": decision,
                "confidence": confidence,
                "requires_review": confidence > 0.7
            }
        )

    def log_kyc_verification(self, customer_id: str, decision: str, confidence: float):
        """Log KYC verification event.
        
        Args:
            customer_id: ID of the customer
            decision: Decision made (APPROVE/REJECT/FLAG)
            confidence: Confidence score
        """
        self.log_event(
            "KYC_VERIFICATION",
            {
                "customer_id": customer_id,
                "decision": decision,
                "confidence": confidence,
                "requires_review": confidence > 0.7
            }
        )

    def log_security_event(self, event_type: str, details: dict):
        """Log security-related event.
        
        Args:
            event_type: Type of security event
            details: Event details
        """
        self.log_event(
            "SECURITY_EVENT",
            {
                "event_type": event_type,
                "details": details
            }
        )
