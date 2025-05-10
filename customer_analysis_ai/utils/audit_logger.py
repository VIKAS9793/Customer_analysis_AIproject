from typing import Dict, Any, List
from datetime import datetime
import json
import logging

class AuditLogger:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.events = []
        self.logger = logging.getLogger('audit')
        self._setup_logger()

    def _setup_logger(self) -> None:
        """Set up the logger with appropriate handlers and formatters."""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler('audit.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        self.logger.setLevel(logging.INFO)

    def log_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Log an event."""
        if not self.config.get('audit_enabled', False):
            return
        
        event = {
            'type': event_type,
            'data': event_data,
            'timestamp': datetime.now().isoformat()
        }
        self.events.append(event)
        self.logger.info(json.dumps(event))

    def log_security_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Log a security event."""
        self.log_event(f'SECURITY_{event_type}', event_data)

    def log_fraud_detection(self, transaction_id: str, decision: str, confidence: float) -> None:
        """Log a fraud detection event."""
        self.log_event('FRAUD_DETECTION', {
            'transaction_id': transaction_id,
            'decision': decision,
            'confidence': confidence
        })

    def get_logs(self, event_type: str = None) -> List[Dict[str, Any]]:
        """Get audit logs, optionally filtered by event type."""
        # Placeholder - in a real implementation, this would read from the log file
        if event_type:
            return [event for event in self.events if event['type'] == event_type]
        return self.events
