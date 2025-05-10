"""
Secure Session Management System

This module implements a secure session management system that:
1. Uses secure session timeouts
2. Implements biometric authentication
3. Follows security best practices
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import secrets
import hashlib
from cryptography.fernet import Fernet
from security.key_management import SecureKeyManager
from security.secrets_manager import SecretsManager
from security.audit_trail import AuditTrail
from security.risk_assessment import RiskAssessment

logger = logging.getLogger(__name__)

class SecureSessionError(Exception):
    """Raised when session operations fail"""
    pass

class SecureSessionManager:
    """Secure session management system"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize secure session manager.
        
        Args:
            config: Configuration containing:
                - session_timeout_minutes: Session timeout in minutes
                - biometric_timeout_minutes: Biometric timeout in minutes
                - max_sessions_per_user: Maximum concurrent sessions
        """
        self.config = config
        
        # Initialize security components
        self.key_manager = SecureKeyManager(config)
        self.secrets_manager = SecretsManager()
        self.audit = AuditTrail(config)
        self.risk_assessment = RiskAssessment(config)
        
        # Security parameters
        self.session_timeout = timedelta(minutes=config.get("session_timeout_minutes", 15))
        self.biometric_timeout = timedelta(minutes=config.get("biometric_timeout_minutes", 5))
        self.max_sessions = config.get("max_sessions_per_user", 5)
        
        # Initialize session storage
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.user_sessions: Dict[str, List[str]] = {}
        
    def _generate_session_id(self) -> str:
        """Generate a secure session ID"""
        return secrets.token_urlsafe(32)  # 256 bits of entropy
        
    def _encrypt_session_data(self, data: Dict[str, Any]) -> str:
        """Encrypt session data securely"""
        session_key = self.key_manager.generate_session_key()
        fernet = Fernet(base64.urlsafe_b64encode(session_key))
        return fernet.encrypt(str(data).encode()).decode()
        
    def _decrypt_session_data(self, encrypted_data: str) -> Dict[str, Any]:
        """Decrypt session data securely"""
        session_key = self.key_manager.generate_session_key()
        fernet = Fernet(base64.urlsafe_b64encode(session_key))
        return eval(fernet.decrypt(encrypted_data.encode()).decode())
        
    def create_session(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new secure session
        
        Args:
            user_id: Unique user identifier
            user_data: User-specific data
            
        Returns:
            Session information including token and expiration
        """
        try:
            # Check risk assessment
            if not self.risk_assessment.is_safe(user_id):
                raise SecureSessionError("High risk user access denied")
                
            # Check max sessions
            if len(self.user_sessions.get(user_id, [])) >= self.max_sessions:
                raise SecureSessionError("Maximum sessions reached")
                
            # Generate session ID
            session_id = self._generate_session_id()
            
            # Create session data
            session_data = {
                "user_id": user_id,
                "created_at": datetime.now(),
                "last_activity": datetime.now(),
                "user_data": user_data,
                "biometric_verified": False
            }
            
            # Encrypt session data
            encrypted_data = self._encrypt_session_data(session_data)
            
            # Store session
            self.sessions[session_id] = {
                "data": encrypted_data,
                "last_access": datetime.now()
            }
            
            # Update user sessions
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = []
            self.user_sessions[user_id].append(session_id)
            
            # Log audit trail
            self.audit.log_event("session_create", {
                "user_id": user_id,
                "session_id": session_id
            })
            
            return {
                "session_id": session_id,
                "expires_at": datetime.now() + self.session_timeout,
                "biometric_required": True
            }
            
        except Exception as e:
            logger.error(f"Failed to create session: {str(e)}")
            raise SecureSessionError(f"Failed to create session: {str(e)}")
            
    def verify_biometric(self, session_id: str, biometric_data: str) -> bool:
        """Verify biometric data for session
        
        Args:
            session_id: Session identifier
            biometric_data: Biometric data to verify
            
        Returns:
            True if biometric verified, False otherwise
        """
        try:
            # Get session data
            session = self.sessions.get(session_id)
            if not session:
                raise SecureSessionError("Invalid session")
                
            # Decrypt session data
            session_data = self._decrypt_session_data(session["data"])
            
            # Check if biometric already verified
            if session_data["biometric_verified"]:
                return True
                
            # Verify biometric data
            if self._verify_biometric_data(biometric_data):
                # Update session data
                session_data["biometric_verified"] = True
                session_data["last_activity"] = datetime.now()
                
                # Encrypt and store updated data
                encrypted_data = self._encrypt_session_data(session_data)
                self.sessions[session_id]["data"] = encrypted_data
                
                # Log audit trail
                self.audit.log_event("biometric_verified", {
                    "session_id": session_id,
                    "user_id": session_data["user_id"]
                })
                
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Failed to verify biometric: {str(e)}")
            return False
            
    def _verify_biometric_data(self, biometric_data: str) -> bool:
        """Verify biometric data using secure comparison
        
        Args:
            biometric_data: Biometric data to verify
            
        Returns:
            True if biometric matches, False otherwise
        """
        try:
            # Get stored biometric template
            stored_template = self.secrets_manager.get_secret("BIOMETRIC_TEMPLATE")
            if not stored_template:
                return False
                
            # Use constant time comparison to prevent timing attacks
            return secrets.compare_digest(biometric_data, stored_template)
            
        except Exception as e:
            logger.error(f"Failed to verify biometric data: {str(e)}")
            return False
            
    def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Validate and return session data
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data if valid, None otherwise
        """
        try:
            # Get session
            session = self.sessions.get(session_id)
            if not session:
                return None
                
            # Check session timeout
            if datetime.now() - session["last_access"] > self.session_timeout:
                self._invalidate_session(session_id)
                return None
                
            # Check biometric timeout
            session_data = self._decrypt_session_data(session["data"])
            if not session_data["biometric_verified"] or \
               datetime.now() - session_data["last_activity"] > self.biometric_timeout:
                return None
                
            # Update last access
            session["last_access"] = datetime.now()
            session_data["last_activity"] = datetime.now()
            
            # Encrypt and store updated data
            encrypted_data = self._encrypt_session_data(session_data)
            self.sessions[session_id]["data"] = encrypted_data
            
            return session_data
            
        except Exception as e:
            logger.error(f"Failed to validate session: {str(e)}")
            return None
            
    def _invalidate_session(self, session_id: str) -> None:
        """Invalidate a session
        
        Args:
            session_id: Session identifier
        """
        try:
            # Get session data
            session = self.sessions.get(session_id)
            if not session:
                return
                
            # Decrypt session data
            session_data = self._decrypt_session_data(session["data"])
            
            # Remove session
            del self.sessions[session_id]
            
            # Update user sessions
            if session_data["user_id"] in self.user_sessions:
                if session_id in self.user_sessions[session_data["user_id"]]:
                    self.user_sessions[session_data["user_id"]].remove(session_id)
                    if not self.user_sessions[session_data["user_id"]]:
                        del self.user_sessions[session_data["user_id"]]
            
            # Log audit trail
            self.audit.log_event("session_invalidate", {
                "session_id": session_id,
                "user_id": session_data["user_id"]
            })
            
        except Exception as e:
            logger.error(f"Failed to invalidate session: {str(e)}")
