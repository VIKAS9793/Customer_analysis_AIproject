"""
FinConnectAI Main Orchestrator - Coordinates all system components
"""

import yaml
import logging
from pathlib import Path
from agents.fraud_agent import FraudAgent
from memory.db_manager import DatabaseManager
from core.safety import AntiHallucinationGuard
from core.metrics import MetricsManager
from feedback.feedback_logger import FeedbackLogger
from datetime import datetime

logger = logging.getLogger(__name__)

class FinConnectAI:
    """Main orchestrator for FinConnectAI system."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the FinConnectAI system.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.setup_logging()
        self.initialize_components()
        self.setup_safety_guards()
        self.setup_monitoring()
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            raise
    
    def setup_logging(self) -> None:
        """Configure system logging."""
        log_level = self.config.get('system', {}).get('log_level', 'INFO')
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def initialize_components(self) -> None:
        """Initialize all system components."""
        # Initialize database
        self.db = DatabaseManager(self.config.get('memory', {}).get('database', 'finconnectai.db'))
        
        # Initialize agents
        self.agents = {
            'fraud': FraudAgent(self.config.get('agents', {}).get('fraud', {})),
            # Add other agents as they're implemented
        }

    def setup_safety_guards(self) -> None:
        """Set up system safety guards."""
        self.safety_guard = AntiHallucinationGuard()
        self.safety_threshold = self.config.get('system', {}).get('safety_threshold', 0.85)
        self.max_retries = self.config.get('system', {}).get('max_retries', 3)

    def setup_monitoring(self) -> None:
        """Set up system monitoring."""
        self.metrics = MetricsManager(self.config.get('monitoring', {}))
        self.error_threshold = self.config.get('monitoring', {}).get('error_threshold', 0.01)
        self.alert_thresholds = self.config.get('monitoring', {}).get('alert_thresholds', {})

    def setup_feedback_system(self) -> None:
        """Set up feedback learning system."""
        self.feedback_logger = FeedbackLogger(self.config.get('feedback', {}))
        self.feedback_threshold = self.config.get('feedback', {}).get('review_required_threshold', 0.8)
        self.max_pending_reviews = self.config.get('feedback', {}).get('max_pending_reviews', 50)

    def learn_from_feedback(self, feedback: dict) -> None:
        """Learn from human feedback to improve system.
        
        Args:
            feedback: Feedback data from human review
        """
        try:
            # Record feedback metrics
            self.metrics.record_task("feedback_processing", True, 0)
            
            # Update agent behavior based on feedback
            if feedback['action'] == 'Reject':
                self._adjust_agent_thresholds(feedback['decision_id'], increase=True)
            elif feedback['action'] == 'Accept':
                self._adjust_agent_thresholds(feedback['decision_id'], increase=False)
                
            # Log learning event
            logger.info(f"Learned from feedback: {feedback['decision_id']}")
            
        except Exception as e:
            logger.error(f"Error learning from feedback: {str(e)}")
            self.metrics.record_task("feedback_processing", False, 0)
            
    def _adjust_agent_thresholds(self, decision_id: str, increase: bool) -> None:
        """Adjust agent thresholds based on feedback.
        
        Args:
            decision_id: ID of the decision being adjusted
            increase: Whether to increase or decrease thresholds
        """
        try:
            # Get original decision
            decision = self.db.get_decision(decision_id)
            
            # Adjust confidence threshold
            current_threshold = self.config['agents']['fraud']['risk_threshold']
            adjustment = 0.05 if increase else -0.05
            new_threshold = min(1.0, max(0.0, current_threshold + adjustment))
            
            # Update configuration
            self.config['agents']['fraud']['risk_threshold'] = new_threshold
            logger.info(f"Adjusted fraud threshold to: {new_threshold}")
            
        except Exception as e:
            logger.error(f"Error adjusting agent thresholds: {str(e)}")

    def get_system_status(self) -> dict:
        """Get current system status and metrics."""
        return {
            'status': 'running',
            'timestamp': datetime.utcnow().isoformat(),
            'pending_reviews': len(self.db.get_pending_decisions()),
            'agents': list(self.agents.keys()),
            'metrics': {
                'request_count': self.metrics.metrics_storage.get('request_count', 0),
                'error_rate': self.metrics.metrics_storage.get('request_error_count', 0) / 
                            max(1, self.metrics.metrics_storage.get('request_count', 0)),
                'pending_feedback': len(self.feedback_logger.get_pending_reviews())
            }
        }

    def process_transaction(self, transaction: dict) -> dict:
        """Process a customer transaction through the system.
        
        Args:
            transaction: Transaction data to process
            
        Returns:
            Dict containing the processing results
        """
        try:
            start_time = time.time()
            
            # Start monitoring
            self.metrics.record_request("transaction", 200, 0)  # Initial record
            
            # Start processing
            logger.info(f"Processing transaction: {transaction.get('id')}")
            
            # Run fraud detection
            fraud_result = self.agents['fraud'].analyze_transaction(transaction)
            
            # Apply safety guards
            fraud_result = self.apply_safety_guards(fraud_result)
            
            # Log decision
            decision_id = self.db.log_decision(fraud_result)
            
            # Record task metrics
            task_latency = time.time() - start_time
            self.metrics.record_task("fraud_detection", True, task_latency)
            
            # Check if human review is needed
            if fraud_result['confidence'] >= self.config['feedback']['review_required_threshold']:
                logger.info(f"Transaction flagged for human review: {transaction.get('id')}")
                return {
                    'status': 'pending_review',
                    'decision_id': decision_id,
                    'reason': 'High risk score'
                }
            
            # If not flagged, auto-approve
            return {
                'status': 'approved',
                'confidence': fraud_result['confidence'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing transaction: {str(e)}")
            self.metrics.record_request("transaction", 500, time.time() - start_time)
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def validate_agent_response(self, response: dict) -> bool:
        """Validate agent response against safety guidelines.
        
        Args:
            response: Agent response to validate
            
        Returns:
            bool: True if response is valid
        """
        try:
            # Check confidence score
            if response.get('confidence', 0) < self.safety_threshold:
                return False
                
            # Verify decision format
            required_fields = ['decision', 'confidence', 'explanation', 'timestamp']
            if not all(field in response for field in required_fields):
                return False
                
            # Check decision validity
            valid_decisions = ['APPROVE', 'REJECT', 'FLAG', 'ERROR']
            if response.get('decision') not in valid_decisions:
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error validating agent response: {str(e)}")
            return False

    def apply_safety_guards(self, decision: dict) -> dict:
        """Apply safety guards to decision.
        
        Args:
            decision: Decision to apply safety guards to
            
        Returns:
            dict: Safe decision
        """
        try:
            # Apply prompt filters if this is a new decision
            if 'prompt' in decision:
                decision = self.safety_guard.apply_prompt_filters(decision)
                
            # Verify response with sources
            decision = self.safety_guard.verify_response_with_sources(decision)
            
            # Add safety metadata
            decision['safety_checked'] = True
            decision['safety_threshold'] = self.safety_threshold
            
            return decision
            
        except Exception as e:
            logger.error(f"Error applying safety guards: {str(e)}")
            return {
                'decision': 'ERROR',
                'confidence': 0.0,
                'explanation': 'Safety check failed',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def process_transaction(self, transaction: dict) -> dict:
        """Process a customer transaction through the system.
        
        Args:
            transaction: Transaction data to process
            
        Returns:
            Dict containing the processing results
        """
        try:
            # Start processing
            logger.info(f"Processing transaction: {transaction.get('id')}")
            
            # Run fraud detection
            fraud_result = self.agents['fraud'].analyze_transaction(transaction)
            
            # Log decision
            decision_id = self.db.log_decision(fraud_result)
            
            # Check if human review is needed
            if fraud_result['confidence'] >= self.config['feedback']['review_required_threshold']:
                logger.info(f"Transaction flagged for human review: {transaction.get('id')}")
                return {
                    'status': 'pending_review',
                    'decision_id': decision_id,
                    'reason': 'High risk score'
                }
            
            # If not flagged, auto-approve
            return {
                'status': 'approved',
                'confidence': fraud_result['confidence'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing transaction: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def handle_feedback(self, decision_id: int, feedback: dict) -> None:
        """Handle feedback from human review.
        
        Args:
            decision_id: ID of the decision being reviewed
            feedback: Feedback data from reviewer
        """
        try:
            self.db.log_feedback(decision_id, feedback)
            self.db.update_decision_status(decision_id, feedback['type'])
            logger.info(f"Feedback processed for decision {decision_id}")
        except Exception as e:
            logger.error(f"Error handling feedback: {str(e)}")
    
    def get_system_status(self) -> dict:
        """Get current system status and metrics."""
        return {
            'status': 'running',
            'timestamp': datetime.utcnow().isoformat(),
            'pending_reviews': len(self.db.get_pending_decisions()),
            'agents': list(self.agents.keys())
        }

def main():
    """Main entry point for the system."""
    try:
        # Initialize system
        finconnect_ai = FinConnectAI()
        
        # Example usage
        test_transaction = {
            'id': 'TX123456',
            'amount': 1500.00,
            'location': 'New York',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        result = customer_ai.process_transaction(test_transaction)
        print(f"Transaction result: {result}")
        
    except Exception as e:
        logger.error(f"System startup failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
