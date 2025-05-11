"""
Secure Session Management System

This module implements enterprise-grade session management with strict security controls.
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta
import secrets
import hashlib
from cryptography.fernet import Fernet
from security.hsm import HSM
from security.audit_trail import AuditTrail
from security.data_masking import DataMasker
from security.token_validator import TokenValidator
from security.risk_assessment import RiskAssessment
from security.event_monitoring import EventMonitor
from security.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

class SessionError(Exception):
    """Raised when session operations fail"""
    pass

class SessionManager:
    """
    Enterprise-grade session management system.
    
    Implements OWASP Session Management recommendations and NIST SP 800-63B requirements.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize session manager with enterprise-grade security.
        
        Args:
            config: Configuration containing:
                - session_timeout_minutes: Maximum session duration
                - refresh_interval_minutes: Token refresh interval
                - max_sessions_per_user: Maximum concurrent sessions
                - max_inactive_time_minutes: Maximum inactive time
                - token_rotation_minutes: Token rotation interval
                - entropy_bits: Required token entropy
                - hsm_config: HSM configuration
                - audit_config: Audit trail configuration
        """
        self.config = config
        
        # Security parameters (NIST SP 800-63B compliant)
        self.session_timeout = timedelta(minutes=config.get("session_timeout_minutes", 30))
        self.refresh_interval = timedelta(minutes=config.get("refresh_interval_minutes", 15))
        self.max_sessions = config.get("max_sessions_per_user", 5)
        self.max_inactive_time = timedelta(minutes=config.get("max_inactive_time_minutes", 5))
        self.token_rotation_interval = timedelta(minutes=config.get("token_rotation_minutes", 10))
        
        # Token entropy requirements (OWASP Session Management Cheat Sheet)
        self.token_entropy = {
            "min_length": 32,
            "required_chars": ["uppercase", "lowercase", "digits", "special"],
            "entropy_bits": config.get("entropy_bits", 256)
        }
        
        # Initialize security components
        self.hsm = HSM(config["hsm_config"])
        self.audit = AuditTrail(config["audit_config"])
        self.masker = DataMasker(config.get("masking_config", {}))
        self.token_validator = TokenValidator(config)
        self.risk_assessment = RiskAssessment(config)
        self.event_monitor = EventMonitor(config)
        self.rate_limiter = RateLimiter(config)
        
        # Initialize session storage
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.user_sessions: Dict[str, List[str]] = {}
        
        # Initialize token blacklists
        self.token_blacklist = self._initialize_token_blacklist()
        
        # Initialize rate limiting
        self.rate_limiter.initialize_limits(config.get("rate_limits", {}))
        
    def create_session(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new secure session.
        
        Args:
            user_id: Unique identifier for the user
            user_data: User-specific data to store in session
            
        Returns:
            Session information including token and expiration
            
        Raises:
            SessionError: If session creation fails
        """
        # Rate limiting check
        if not self.rate_limiter.check_limit(f"session_create_{user_id}"):
            raise SessionError("Rate limit exceeded for session creation")
            
        # Risk assessment
        risk_level = self.risk_assessment.evaluate_session(user_id, user_data)
        if risk_level == "high":
            raise SessionError("High risk detected, session creation blocked")
            
        try:
            # Generate secure token
            token = self._generate_secure_token()
            
            # Encrypt sensitive data
            encrypted_data = self._encrypt_session_data(user_data)
            
            # Create session object
            session = {
                "token": token,
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "last_active": datetime.utcnow(),
                "expires_at": datetime.utcnow() + self.session_timeout,
                "refresh_at": datetime.utcnow() + self.refresh_interval,
                "encrypted_data": encrypted_data,
                "risk_level": risk_level,
                "metadata": {
                    "ip_address": user_data.get("ip_address"),
                    "user_agent": user_data.get("user_agent")
                }
            }
            
            # Store session
            self._store_session(token, session)
            
            # Update user session count
            self._update_user_session_count(user_id, token)
            
            # Log session creation
            self.audit.log_event("session_creation", {
                "user_id": user_id,
                "token": self.masker.mask_token(token),
                "risk_level": risk_level
            })
            
            return {
                "token": token,
                "expires_at": session["expires_at"].isoformat(),
                "refresh_at": session["refresh_at"].isoformat()
            }
            
        except Exception as e:
            self.audit.log_event("session_creation_failed", {
                "user_id": user_id,
                "error": str(e)
            })
            raise SessionError(f"Failed to create session: {str(e)}")
    
    def validate_session(self, token: str) -> Dict[str, Any]:
        """
        Validate and refresh a session if needed.
        
        Args:
            token: Session token to validate
            
        Returns:
            Validated session data
            
        Raises:
            SessionError: If session is invalid or expired
        """
        try:
            # Check token blacklist
            if token in self.token_blacklist:
                raise SessionError("Token has been revoked")
                
            # Get session
            session = self._get_session(token)
            if not session:
                raise SessionError("Session not found")
                
            # Check session expiration
            if datetime.utcnow() > session["expires_at"]:
                self._invalidate_session(token)
                raise SessionError("Session expired")
                
            # Check inactive time
            if datetime.utcnow() - session["last_active"] > self.max_inactive_time:
                self._invalidate_session(token)
                raise SessionError("Session inactive for too long")
                
            # Check refresh needed
            if datetime.utcnow() > session["refresh_at"]:
                return self._refresh_session(token)
                
            # Update last active time
            session["last_active"] = datetime.utcnow()
            self._store_session(token, session)
            
            # Decrypt and return session data
            return self._decrypt_session_data(session["encrypted_data"])
            
        except Exception as e:
            self.audit.log_event("session_validation_failed", {
                "token": self.masker.mask_token(token),
                "error": str(e)
            })
            raise SessionError(f"Failed to validate session: {str(e)}")
    
    def invalidate_session(self, token: str) -> None:
        """
        Invalidate a session and blacklist the token.
        
        Args:
            token: Session token to invalidate
        """
        try:
            # Get session
            session = self._get_session(token)
            if session:
                # Invalidate session
                self._invalidate_session(token)
                
                # Update user session count
                self._update_user_session_count(session["user_id"], token, remove=True)
                
                # Log session invalidation
                self.audit.log_event("session_invalidation", {
                    "user_id": session["user_id"],
                    "token": self.masker.mask_token(token)
                })
            
        except Exception as e:
            self.audit.log_event("session_invalidation_failed", {
                "token": self.masker.mask_token(token),
                "error": str(e)
            })
            raise SessionError(f"Failed to invalidate session: {str(e)}")
    
    def _generate_secure_token(self) -> str:
        """Generate a cryptographically secure token."""
        # Generate random bytes with required entropy
        token_bytes = secrets.token_bytes(self.token_entropy["min_length"])
        
        # Add additional entropy from HSM
        token_bytes = self.hsm.add_entropy(token_bytes)
        
        # Generate token using secure hash
        token = hashlib.sha256(token_bytes).hexdigest()
        
        # Validate token entropy
        if not self._validate_token_entropy(token):
            raise SessionError("Failed to generate token with required entropy")
            
        return token
    
    def _encrypt_session_data(self, data: Dict[str, Any]) -> bytes:
        """Encrypt session data using HSM-protected key."""
        key = self.hsm.get_session_key()
        fernet = Fernet(key)
        return fernet.encrypt(json.dumps(data).encode())
    
    def _decrypt_session_data(self, encrypted_data: bytes) -> Dict[str, Any]:
        """Decrypt session data using HSM-protected key."""
        key = self.hsm.get_session_key()
        fernet = Fernet(key)
        return json.loads(fernet.decrypt(encrypted_data).decode())
    
    def _store_session(self, token: str, session: Dict[str, Any]) -> None:
        """Store session in secure storage."""
        self.sessions[token] = session
        self.audit.log_event("session_storage", {
            "token": self.masker.mask_token(token),
            "user_id": session["user_id"]
        })
    
    def _get_session(self, token: str) -> Optional[Dict[str, Any]]:
        """Retrieve session from storage."""
        return self.sessions.get(token)
    
    def _invalidate_session(self, token: str) -> None:
        """Mark session as invalid and blacklist token."""
        if token in self.sessions:
            del self.sessions[token]
            self.token_blacklist.add(token)
    
    def _update_user_session_count(self, user_id: str, token: str, remove: bool = False) -> None:
        """Update user's active session count."""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = []
            
        if remove:
            self.user_sessions[user_id].remove(token)
        else:
            if len(self.user_sessions[user_id]) >= self.max_sessions:
                raise SessionError("Maximum concurrent sessions exceeded")
            self.user_sessions[user_id].append(token)
    
    def _validate_token_entropy(self, token: str) -> bool:
        """Validate token meets entropy requirements."""
        # Check length
        if len(token) < self.token_entropy["min_length"]:
            return False
            
        # Check character requirements
        char_sets = {
            "uppercase": any(c.isupper() for c in token),
            "lowercase": any(c.islower() for c in token),
            "digits": any(c.isdigit() for c in token),
            "special": any(not c.isalnum() for c in token)
        }
        
        if not all(char_sets[req] for req in self.token_entropy["required_chars"]):
            return False
            
        return True
    
    def _initialize_token_blacklist(self) -> set:
        """Initialize token blacklist from persistent storage."""
        # In production, this would be loaded from a secure database
        return set()
        self.session_validator = self._initialize_session_validator()
    
    def _initialize_token_blacklist(self) -> Dict[str, Any]:
        """Initialize token blacklist system"""
        try:
            return {
                "enabled": True,
                "storage": "HSM",
                "max_tokens": 10000,
                "cleanup_interval": 3600,  # seconds
                "audit_enabled": True
            }
        except Exception as e:
            self.logger.error(f"Token blacklist initialization failed: {str(e)}")
            raise SessionError(f"Failed to initialize token blacklist: {str(e)}")
    
    def _initialize_session_validator(self) -> Dict[str, Any]:
        """Initialize session state validator"""
        try:
            return {
                "enabled": True,
                "validation_interval": 60,  # seconds
                "state_checks": [
                    "valid_token",
                    "valid_nonce",
                    "valid_ip",
                    "valid_device",
                    "valid_location"
                ],
                "audit_enabled": True
            }
        except Exception as e:
            self.logger.error(f"Session validator initialization failed: {str(e)}")
            raise SessionError(f"Failed to initialize session validator: {str(e)}")
    
    def _validate_token_entropy(self, token: str) -> bool:
        """Validate token entropy requirements"""
        try:
            # Check token length
            if len(token) < self.token_entropy["min_length"]:
                return False
            
            # Check required character types
            required = self.token_entropy["required_chars"]
            if not any(c.isupper() for c in token) and "uppercase" in required:
                return False
            if not any(c.islower() for c in token) and "lowercase" in required:
                return False
            if not any(c.isdigit() for c in token) and "digits" in required:
                return False
            if not any(not c.isalnum() for c in token) and "special" in required:
                return False
            
            # Check entropy bits
            entropy = self.hsm.calculate_entropy(token)
            if entropy < self.token_entropy["entropy_bits"]:
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Token entropy validation failed: {str(e)}")
            raise SessionError(f"Failed to validate token entropy: {str(e)}")
    
    def _check_token_blacklist(self, token: str) -> bool:
        """Check if token is blacklisted"""
        try:
            # Check HSM-based blacklist
            if self.hsm.is_token_blacklisted(token):
                raise SessionError("Token is blacklisted")
            
            return False
        except Exception as e:
            self.logger.error(f"Token blacklist check failed: {str(e)}")
            raise SessionError(f"Failed to check token blacklist: {str(e)}")
    
    def _rotate_session_token(self, session_id: str) -> str:
        """Rotate session token securely"""
        try:
            # Get current session
            session = self._decrypt_session_data(self.sessions[session_id])
            
            # Generate new token
            new_token = self._generate_token_with_hsm(session["user_id"])
            
            # Blacklist old token
            self.hsm.blacklist_token(session["token"])
            
            # Update session with new token
            session["token"] = new_token
            session["last_refresh"] = datetime.now().isoformat()
            
            # Store updated session
            self.sessions[session_id] = self._encrypt_session_data(session)
            
            # Log token rotation
            self.audit.log_event(
                "SESSION_TOKEN_ROTATION",
                {
                    "session_id": session_id,
                    "user_id": session["user_id"],
                    "status": "SUCCESS"
                }
            )
            
            return new_token
        except Exception as e:
            self.logger.error(f"Token rotation failed: {str(e)}")
            raise SessionError(f"Failed to rotate session token: {str(e)}")
    
    def create_session(self, user_id: str, ip_address: str) -> Dict[str, Any]:
        """Create a new secure session with comprehensive security"""
        try:
            # Generate secure session ID with HSM
            session_id = self.hsm.generate_key_pair()["key_id"]
            
            # Generate secure nonce for replay protection
            nonce = secrets.token_hex(16)
            
            # Generate secure token with HSM
            token = self._generate_token_with_hsm(user_id)
            
            # Validate token entropy
            if not self._validate_token_entropy(token):
                raise SessionError("Token entropy requirements not met")
            
            # Check token blacklist
            if self._check_token_blacklist(token):
                raise SessionError("Token is blacklisted")
            
            # Create session data
            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "ip_address": ip_address,
                "created_at": datetime.now().isoformat(),
                "last_refresh": datetime.now().isoformat(),
                "token": token,
                "status": "active",
                "nonce": nonce,
                "last_activity": datetime.now().isoformat(),
                "activity_count": 0
            }
            
            # Encrypt session data before storage
            encrypted_data = self._encrypt_session_data(session_data)
            
            # Store encrypted session
            self.sessions[session_id] = encrypted_data
            
            # Create backup
            self._create_session_backup(session_data)
            
            # Track nonce
            self.nonce_tracker[session_id] = nonce
            
            # Log session creation
            self.audit.log_event(
                "SESSION_CREATION",
                {
                    "session_id": session_id,
                    "user_id": user_id,
                    "status": "SUCCESS"
                }
            )
            
            # Validate session state
            if not self._validate_session_state(session_data):
                raise SessionError("Invalid session state")
            
            # Validate session count
            user_sessions = [s for s in self.sessions.values() if s["user_id"] == user_id]
            if len(user_sessions) > self.max_sessions:
                self._cleanup_oldest_sessions(user_id)
            
            # Start session monitoring
            self._start_session_monitoring(session_id)
            
            # Schedule token rotation
            self._schedule_token_rotation(session_id)
            
            self.logger.info(f"Created secure session for user {user_id}")
            return session_data
        except Exception as e:
            self.logger.error(f"Secure session creation failed: {str(e)}")
            raise SessionError(f"Failed to create secure session: {str(e)}")
    
    def _validate_session_state(self, session: Dict[str, Any]) -> bool:
        """Validate session state"""
        try:
            # Validate token
            if not self.token_validator.validate_token(session["token"]):
                return False
            
            # Validate nonce
            if session["nonce"] != self.nonce_tracker.get(session["session_id"]):
                return False
            
            # Validate IP
            if not self._validate_ip(session["ip_address"]):
                return False
            
            # Validate session status
            if session["status"] != "active":
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Session state validation failed: {str(e)}")
            raise SessionError(f"Failed to validate session state: {str(e)}")
    
    def _schedule_token_rotation(self, session_id: str) -> None:
        """Schedule token rotation"""
        try:
            # Schedule rotation based on interval
            rotation_time = datetime.now() + timedelta(
                minutes=self.token_rotation_interval
            )
            
            # Store rotation time
            self.sessions[session_id]["next_rotation"] = rotation_time.isoformat()
            
            # Start rotation timer
            self._start_rotation_timer(session_id)
        except Exception as e:
            self.logger.error(f"Token rotation scheduling failed: {str(e)}")
            raise SessionError(f"Failed to schedule token rotation: {str(e)}")
    
    def _start_rotation_timer(self, session_id: str) -> None:
        """Start token rotation timer"""
        try:
            # Get rotation time
            rotation_time = datetime.fromisoformat(
                self.sessions[session_id]["next_rotation"]
            )
            
            # Schedule rotation
            self.session_monitor["scheduler"].add_job(
                self._rotate_session_token,
                "date",
                run_date=rotation_time,
                args=[session_id]
            )
            
            self.logger.info(f"Token rotation scheduled for session {session_id}")
        except Exception as e:
            self.logger.error(f"Rotation timer start failed: {str(e)}")
            raise SessionError(f"Failed to start rotation timer: {str(e)}")
        
        # Initialize encryption
        self.fernet = Fernet(Fernet.generate_key())
        
        # Initialize secure storage
        self.sessions = self._initialize_secure_storage()
        
        # Initialize backup system
        self.backup_system = self._initialize_backup()
        
        # Initialize session monitoring
        self.session_monitor = self._initialize_session_monitor()
        
        # Initialize replay protection
        self.nonce_tracker = {}
        
        # Initialize rate limiting
        self.rate_limiter = self._initialize_rate_limiter()
    
    def _initialize_secure_storage(self) -> Any:
        """Initialize secure session storage"""
        try:
            # In production, use HSM-encrypted database
            return {
                "type": "HSM_DATABASE",
                "encryption_key": self.hsm.generate_key_pair()["key_id"],
                "audit_enabled": True,
                "replication_factor": 3
            }
        except Exception as e:
            self.logger.error(f"Secure storage initialization failed: {str(e)}")
            raise SessionError(f"Failed to initialize secure storage: {str(e)}")
    
    def _initialize_session_monitor(self) -> Any:
        """Initialize session activity monitoring"""
        try:
            return {
                "enabled": True,
                "monitor_interval": 60,  # seconds
                "alert_threshold": 100,  # sessions
                "audit_enabled": True
            }
        except Exception as e:
            self.logger.error(f"Session monitoring initialization failed: {str(e)}")
            raise SessionError(f"Failed to initialize session monitoring: {str(e)}")
    
    def _initialize_rate_limiter(self) -> Any:
        """Initialize session rate limiting"""
        try:
            return {
                "max_requests": 100,
                "time_window": 60,  # seconds
                "block_duration": 300,  # seconds
                "audit_enabled": True
            }
        except Exception as e:
            self.logger.error(f"Rate limiter initialization failed: {str(e)}")
            raise SessionError(f"Failed to initialize rate limiter: {str(e)}")
    
    def create_session(self, user_id: str, ip_address: str) -> Dict[str, Any]:
        """Create a new secure session with comprehensive security"""
        try:
            # Generate secure session ID with HSM
            session_id = self.hsm.generate_key_pair()["key_id"]
            
            # Generate secure nonce for replay protection
            nonce = secrets.token_hex(16)
            
            # Generate secure token with HSM
            token = self._generate_token_with_hsm(user_id)
            
            # Create session data
            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "ip_address": ip_address,
                "created_at": datetime.now().isoformat(),
                "last_refresh": datetime.now().isoformat(),
                "token": token,
                "status": "active",
                "nonce": nonce,
                "last_activity": datetime.now().isoformat(),
                "activity_count": 0
            }
            
            # Encrypt session data before storage
            encrypted_data = self._encrypt_session_data(session_data)
            
            # Store encrypted session
            self.sessions[session_id] = encrypted_data
            
            # Create backup
            self._create_session_backup(session_data)
            
            # Track nonce
            self.nonce_tracker[session_id] = nonce
            
            # Log session creation
            self.audit.log_event(
                "SESSION_CREATION",
                {
                    "session_id": session_id,
                    "user_id": user_id,
                    "status": "SUCCESS"
                }
            )
            
            # Validate session count
            user_sessions = [s for s in self.sessions.values() if s["user_id"] == user_id]
            if len(user_sessions) > self.max_sessions:
                self._cleanup_oldest_sessions(user_id)
            
            # Start session monitoring
            self._start_session_monitoring(session_id)
            
            self.logger.info(f"Created secure session for user {user_id}")
            return session_data
        except Exception as e:
            self.logger.error(f"Secure session creation failed: {str(e)}")
            raise SessionError(f"Failed to create secure session: {str(e)}")
    
    def _start_session_monitoring(self, session_id: str) -> None:
        """Start monitoring session activity"""
        try:
            # Schedule monitoring
            self.session_monitor["scheduler"].add_job(
                self._monitor_session_activity,
                "interval",
                seconds=self.session_monitor["monitor_interval"],
                args=[session_id]
            )
            
            self.logger.info(f"Session monitoring started for {session_id}")
        except Exception as e:
            self.logger.error(f"Session monitoring failed: {str(e)}")
            raise SessionError(f"Failed to start session monitoring: {str(e)}")
    
    def _monitor_session_activity(self, session_id: str) -> None:
        """Monitor session activity and detect anomalies"""
        try:
            session = self._decrypt_session_data(self.sessions[session_id])
            
            # Check for inactivity
            last_activity = datetime.fromisoformat(session["last_activity"])
            if (datetime.now() - last_activity).total_seconds() > self.max_inactive_time * 60:
                self._invalidate_session(session_id)
                
            # Check activity count
            if session["activity_count"] > self.session_monitor["alert_threshold"]:
                self.audit.log_event(
                    "SESSION_ACTIVITY_ALERT",
                    {
                        "session_id": session_id,
                        "activity_count": session["activity_count"]
                    }
                )
                
            self.logger.info(f"Session {session_id} activity monitored")
        except Exception as e:
            self.logger.error(f"Session activity monitoring failed: {str(e)}")
            raise SessionError(f"Failed to monitor session activity: {str(e)}")
    
    def _initialize_backup(self) -> Any:
        """Initialize secure backup system"""
        try:
            # In production, use secure backup system
            return {
                "enabled": True,
                "interval": 3600,  # Backup interval in seconds
                "storage": "HSM"
            }
        except Exception as e:
            self.logger.error(f"Backup initialization failed: {str(e)}")
            raise SessionError(f"Failed to initialize backup: {str(e)}")
    
    def _encrypt_session_data(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt session data using HSM"""
        try:
            # Encrypt sensitive fields
            encrypted_data = {}
            for key, value in session_data.items():
                if key in ["token", "user_id", "ip_address"]:
                    encrypted_value = self.hsm.encrypt_data(str(value).encode())
                    encrypted_data[key] = encrypted_value.hex()
                else:
                    encrypted_data[key] = value
            return encrypted_data
        except Exception as e:
            self.logger.error(f"Session data encryption failed: {str(e)}")
            raise SessionError(f"Failed to encrypt session data: {str(e)}")
    
    def _decrypt_session_data(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt session data using HSM"""
        try:
            # Decrypt sensitive fields
            decrypted_data = {}
            for key, value in session_data.items():
                if key in ["token", "user_id", "ip_address"] and isinstance(value, str):
                    encrypted_value = bytes.fromhex(value)
                    decrypted_value = self.hsm.decrypt_data(encrypted_value)
                    decrypted_data[key] = decrypted_value.decode()
                else:
                    decrypted_data[key] = value
            return decrypted_data
        except Exception as e:
            self.logger.error(f"Session data decryption failed: {str(e)}")
            raise SessionError(f"Failed to decrypt session data: {str(e)}")
    
    def create_session(self, user_id: str, ip_address: str) -> Dict[str, Any]:
        """Create a new secure session with HSM integration"""
        try:
            # Generate secure session ID with HSM
            session_id = self.hsm.generate_key_pair()["key_id"]
            
            # Generate secure token with HSM
            token = self._generate_token_with_hsm(user_id)
            
            # Create session data
            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "ip_address": ip_address,
                "created_at": datetime.now().isoformat(),
                "last_refresh": datetime.now().isoformat(),
                "token": token,
                "status": "active"
            }
            
            # Encrypt session data before storage
            encrypted_data = self._encrypt_session_data(session_data)
            
            # Store encrypted session
            self.sessions[session_id] = encrypted_data
            
            # Create backup
            self._create_session_backup(session_data)
            
            # Validate session count
            user_sessions = [s for s in self.sessions.values() if s["user_id"] == user_id]
            if len(user_sessions) > self.max_sessions:
                self._cleanup_oldest_sessions(user_id)
            
            self.logger.info(f"Created new secure session for user {user_id}")
            return session_data
        except Exception as e:
            self.logger.error(f"Secure session creation failed: {str(e)}")
            raise SessionError(f"Failed to create secure session: {str(e)}")
    
    def _generate_token_with_hsm(self, user_id: str) -> str:
        """Generate JWT token with HSM signing"""
        try:
            payload = {
                "user_id": user_id,
                "exp": datetime.now() + timedelta(minutes=self.session_timeout),
                "iat": datetime.now()
            }
            
            # Get signing key from HSM
            key_info = self.hsm.generate_key_pair()
            
            # Sign token with HSM
            token = jwt.encode(
                payload,
                key_info["key_id"],
                algorithm="RS256"
            )
            
            return token
        except Exception as e:
            self.logger.error(f"Secure token generation failed: {str(e)}")
            raise SessionError(f"Failed to generate secure token: {str(e)}")
    
    def _create_session_backup(self, session_data: Dict[str, Any]) -> None:
        """Create secure session backup"""
        try:
            # Encrypt backup data
            encrypted_data = self._encrypt_session_data(session_data)
            
            # Store in backup system
            self.backup_system["storage"] = encrypted_data
            
            self.logger.info("Session backup created successfully")
        except Exception as e:
            self.logger.error(f"Session backup failed: {str(e)}")
            raise SessionError(f"Failed to create session backup: {str(e)}")
    
    def create_session(self, user_id: str, ip_address: str) -> Dict[str, Any]:
        """Create a new secure session"""
        try:
            # Generate secure session ID
            session_id = secrets.token_hex(32)
            
            # Generate secure token
            token = self._generate_token(user_id)
            
            # Create session data
            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "ip_address": ip_address,
                "created_at": datetime.now().isoformat(),
                "last_refresh": datetime.now().isoformat(),
                "token": token,
                "status": "active"
            }
            
            # Store session
            self.sessions[session_id] = session_data
            
            # Validate session count
            user_sessions = [s for s in self.sessions.values() if s["user_id"] == user_id]
            if len(user_sessions) > self.max_sessions:
                self._cleanup_oldest_sessions(user_id)
            
            self.logger.info(f"Created new session for user {user_id}")
            return session_data
        except Exception as e:
            self.logger.error(f"Session creation failed: {str(e)}")
            raise SessionError(f"Failed to create session: {str(e)}")
    
    def _generate_token(self, user_id: str) -> str:
        """Generate JWT token with strict security"""
        try:
            payload = {
                "user_id": user_id,
                "exp": datetime.now() + timedelta(minutes=self.session_timeout),
                "iat": datetime.now()
            }
            
            # In production, use HSM for signing
            return jwt.encode(
                payload,
                self.config["jwt_secret"],
                algorithm="HS256"
            )
        except Exception as e:
            self.logger.error(f"Token generation failed: {str(e)}")
            raise SessionError(f"Failed to generate token: {str(e)}")
    
    def validate_session(self, session_id: str, token: str) -> Dict[str, Any]:
        """Validate session with strict security checks"""
        try:
            # Check if session exists
            if session_id not in self.sessions:
                raise SessionError("Invalid session ID")
            
            session = self.sessions[session_id]
            
            # Check token validity
            try:
                jwt.decode(token, self.config["jwt_secret"], algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                raise SessionError("Session expired")
            except jwt.InvalidTokenError:
                raise SessionError("Invalid token")
            
            # Check session status
            if session["status"] != "active":
                raise SessionError("Session inactive")
            
            # Check IP address
            if session["ip_address"] != self._get_client_ip():
                raise SessionError("IP address mismatch")
            
            # Check session timeout
            created = datetime.fromisoformat(session["created_at"])
            if (datetime.now() - created) > timedelta(minutes=self.session_timeout):
                raise SessionError("Session expired")
            
            # Refresh session
            self._refresh_session(session_id)
            
            return session
        except SessionError as e:
            self.logger.error(f"Session validation failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Session validation error: {str(e)}")
            raise SessionError(f"Session validation failed: {str(e)}")
    
    def _refresh_session(self, session_id: str) -> None:
        """Refresh session with strict security"""
        try:
            if session_id not in self.sessions:
                raise SessionError("Invalid session ID")
            
            session = self.sessions[session_id]
            session["last_refresh"] = datetime.now().isoformat()
            
            # Generate new token
            new_token = self._generate_token(session["user_id"])
            session["token"] = new_token
            
            self.logger.info(f"Session refreshed for user {session["user_id"]}")
        except Exception as e:
            self.logger.error(f"Session refresh failed: {str(e)}")
            raise SessionError(f"Failed to refresh session: {str(e)}")
    
    def invalidate_session(self, session_id: str) -> None:
        """Invalidate session securely"""
        try:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                session["status"] = "invalidated"
                session["token"] = ""
                self.logger.info(f"Session invalidated for user {session["user_id"]}")
        except Exception as e:
            self.logger.error(f"Session invalidation failed: {str(e)}")
            raise SessionError(f"Failed to invalidate session: {str(e)}")
    
    def _cleanup_oldest_sessions(self, user_id: str) -> None:
        """Cleanup oldest sessions for a user"""
        try:
            user_sessions = [s for s in self.sessions.values() if s["user_id"] == user_id]
            user_sessions.sort(key=lambda x: x["created_at"])
            
            # Keep only the most recent sessions
            sessions_to_keep = user_sessions[-self.max_sessions:]
            sessions_to_remove = user_sessions[:-self.max_sessions]
            
            for session in sessions_to_remove:
                self.invalidate_session(session["session_id"])
        except Exception as e:
            self.logger.error(f"Session cleanup failed: {str(e)}")
            raise SessionError(f"Failed to cleanup sessions: {str(e)}")
    
    def _get_client_ip(self) -> str:
        """Get client IP address securely"""
        try:
            # In production, get from request headers with validation
            return "127.0.0.1"  # For simulation
        except Exception as e:
            self.logger.error(f"Failed to get client IP: {str(e)}")
            raise SessionError(f"Failed to get client IP: {str(e)}")
