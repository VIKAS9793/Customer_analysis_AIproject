"""
API Security System

This module implements enterprise-grade API security controls.
"""

from typing import Dict, Any, Optional, List
import logging
import jwt
from datetime import datetime, timedelta
import hashlib
from cryptography.fernet import Fernet
from security.hsm import HSM
from security.key_exchange import KeyExchange
from security.audit_trail import AuditTrail
from security.data_masking import DataMasker

class APIError(Exception):
    """Raised when API security operations fail"""
    pass

class APISecurity:
    def __init__(self, config: Dict[str, Any]):
        """Initialize API security with comprehensive security features"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Security parameters
        self.token_expiration = config.get("token_expiration_minutes", 30)
        self.rate_limits = config.get("rate_limits", {
            "max_requests": 100,
            "time_window_seconds": 60,
            "block_duration": 300  # seconds
        })
        
        # Initialize security components
        self.hsm = HSM(config)
        self.key_exchange = KeyExchange(config)
        self.fernet = Fernet(Fernet.generate_key())
        self.audit = AuditTrail(config)
        self.masker = DataMasker(config)
        
        # Initialize secure storage
        self.secure_storage = self._initialize_secure_storage()
        
        # API endpoint security definitions
        self.endpoint_security = {
            "/api/v1/auth": {
                "methods": ["POST"],
                "authentication": "basic",
                "rate_limit": True,
                "encryption": True,
                "audit": True,
                "version": "1.0",
                "request_validation": True,
                "response_validation": True
            },
            "/api/v1/transactions": {
                "methods": ["GET", "POST"],
                "authentication": "jwt",
                "rate_limit": True,
                "roles": ["admin", "analyst"],
                "encryption": True,
                "audit": True,
                "version": "1.0",
                "request_validation": True,
                "response_validation": True,
                "data_masking": True
            },
            "/api/v1/reports": {
                "methods": ["GET"],
                "authentication": "jwt",
                "rate_limit": True,
                "roles": ["admin", "reviewer"],
                "encryption": True,
                "audit": True,
                "version": "1.0",
                "request_validation": True,
                "response_validation": True,
                "data_masking": True
            }
        }
        
        # Initialize API versioning
        self.api_versions = self._initialize_api_versions()
        
        # Initialize request correlation
        self.request_correlation = self._initialize_request_correlation()
        
        # Initialize response validation
        self.response_validator = self._initialize_response_validator()
    
    def _initialize_api_versions(self) -> Dict[str, Any]:
        """Initialize API versioning"""
        try:
            return {
                "current_version": "1.0",
                "supported_versions": ["1.0"],
                "version_policy": {
                    "deprecation_window": 90,  # days
                    "notification_window": 30,  # days
                    "audit_enabled": True
                }
            }
        except Exception as e:
            self.logger.error(f"API versioning initialization failed: {str(e)}")
            raise APIError(f"Failed to initialize API versioning: {str(e)}")
    
    def _initialize_request_correlation(self) -> Dict[str, Any]:
        """Initialize request correlation"""
        try:
            return {
                "enabled": True,
                "correlation_id_length": 32,
                "audit_enabled": True,
                "storage": "HSM"
            }
        except Exception as e:
            self.logger.error(f"Request correlation initialization failed: {str(e)}")
            raise APIError(f"Failed to initialize request correlation: {str(e)}")
    
    def _initialize_response_validator(self) -> Dict[str, Any]:
        """Initialize response validation"""
        try:
            return {
                "schema_validation": True,
                "data_integrity": True,
                "encryption_validation": True,
                "audit_enabled": True
            }
        except Exception as e:
            self.logger.error(f"Response validation initialization failed: {str(e)}")
            raise APIError(f"Failed to initialize response validation: {str(e)}")
    
    def _validate_api_version(self, request: Dict[str, Any]) -> bool:
        """Validate API version with strict security checks"""
        try:
            requested_version = request.get("api_version", "1.0")
            
            # Check if version is supported
            if requested_version not in self.api_versions["supported_versions"]:
                raise APIError(f"API version {requested_version} not supported")
            
            # Check for deprecated versions
            if requested_version != self.api_versions["current_version"]:
                self._log_deprecation_warning(requested_version)
                
            # Validate version format
            if not self._validate_version_format(requested_version):
                raise APIError("Invalid API version format")
                
            # Check version compatibility
            if not self._check_version_compatibility(requested_version):
                raise APIError("Incompatible API version")
            
            return True
        except APIError as e:
            self.logger.error(f"API version validation failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"API version error: {str(e)}")
            raise APIError(f"API version error: {str(e)}")
    
    def _validate_version_format(self, version: str) -> bool:
        """Validate API version format"""
        try:
            # Check semantic versioning format
            parts = version.split('.')
            if len(parts) != 3:
                return False
                
            # Validate each part is numeric
            for part in parts:
                if not part.isdigit():
                    return False
                    
            # Validate version numbers
            major, minor, patch = map(int, parts)
            if major < 0 or minor < 0 or patch < 0:
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"Version format validation failed: {str(e)}")
            raise APIError(f"Failed to validate version format: {str(e)}")
    
    def _check_version_compatibility(self, version: str) -> bool:
        """Check API version compatibility"""
        try:
            # Get current version
            current_version = self.api_versions["current_version"]
            
            # Compare major versions
            current_major = int(current_version.split('.')[0])
            requested_major = int(version.split('.')[0])
            
            # Major version mismatch
            if current_major != requested_major:
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"Version compatibility check failed: {str(e)}")
            raise APIError(f"Failed to check version compatibility: {str(e)}")
    
    def _generate_correlation_id(self) -> str:
        """Generate secure correlation ID with HSM"""
        try:
            # Generate secure ID with HSM
            correlation_id = self.hsm.generate_key_pair()["key_id"]
            
            # Validate ID format
            if not self._validate_correlation_id_format(correlation_id):
                raise APIError("Invalid correlation ID format")
                
            # Store in correlation system
            self.request_correlation["storage"] = correlation_id
            
            # Log correlation ID generation
            self.audit.log_event(
                "CORRELATION_ID_GENERATION",
                {
                    "correlation_id": correlation_id,
                    "status": "SUCCESS"
                }
            )
            
            return correlation_id
        except Exception as e:
            self.logger.error(f"Correlation ID generation failed: {str(e)}")
            raise APIError(f"Failed to generate correlation ID: {str(e)}")
    
    def _validate_correlation_id_format(self, correlation_id: str) -> bool:
        """Validate correlation ID format"""
        try:
            # Check length
            if len(correlation_id) != self.request_correlation["correlation_id_length"]:
                return False
                
            # Check character set
            if not all(c in "0123456789abcdef" for c in correlation_id.lower()):
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"Correlation ID format validation failed: {str(e)}")
            raise APIError(f"Failed to validate correlation ID format: {str(e)}")
    
    def _validate_request(self, request: Dict[str, Any], endpoint: str) -> bool:
        """Validate API request with comprehensive security checks"""
        try:
            # Get endpoint security config
            security_config = self.endpoint_security[endpoint]
            
            # Validate request size
            if not self._validate_request_size(request):
                raise APIError("Request size exceeds maximum allowed")
                
            # Validate request rate
            if not self._validate_request_rate(endpoint, request):
                raise APIError("Request rate limit exceeded")
                
            # Validate request schema
            if security_config["request_validation"]:
                self._validate_request_schema(request, endpoint)
            
            # Validate data masking requirements
            if security_config["data_masking"]:
                self._validate_data_masking(request)
            
            # Validate encryption
            if security_config["encryption"]:
                self._validate_request_encryption(request)
            
            # Validate request signature
            if not self._validate_request_signature(request):
                raise APIError("Invalid request signature")
                
            return True
        except Exception as e:
            self.logger.error(f"Request validation failed: {str(e)}")
            raise APIError(f"Failed to validate request: {str(e)}")
    
    def _validate_request_size(self, request: Dict[str, Any]) -> bool:
        """Validate request size"""
        try:
            # Get request size
            request_size = len(str(request))
            
            # Check against maximum allowed size
            max_size = self.config.get("max_request_size_bytes", 1048576)  # 1MB default
            if request_size > max_size:
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"Request size validation failed: {str(e)}")
            raise APIError(f"Failed to validate request size: {str(e)}")
    
    def _validate_request_rate(self, endpoint: str, request: Dict[str, Any]) -> bool:
        """Validate request rate per endpoint"""
        try:
            # Get rate limit config
            rate_limit = self.rate_limits[endpoint]
            
            # Check request count in time window
            current_time = datetime.now()
            window_start = current_time - timedelta(seconds=rate_limit["time_window_seconds"])
            
            # Get requests in window
            requests_in_window = self._get_requests_in_window(endpoint, window_start)
            
            # Check if rate limit exceeded
            if len(requests_in_window) >= rate_limit["max_requests"]:
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"Request rate validation failed: {str(e)}")
            raise APIError(f"Failed to validate request rate: {str(e)}")
    
    def _validate_request_signature(self, request: Dict[str, Any]) -> bool:
        """Validate request signature"""
        try:
            # Get signature from request
            signature = request.get("signature")
            if not signature:
                return False
                
            # Get signing key from HSM
            key_id = request.get("signing_key_id")
            if not key_id:
                return False
                
            # Validate signature using HSM
            if not self.hsm.validate_signature(request, signature, key_id):
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"Request signature validation failed: {str(e)}")
            raise APIError(f"Failed to validate request signature: {str(e)}")
    
    def _get_requests_in_window(self, endpoint: str, window_start: datetime) -> List[Dict[str, Any]]:
        """Get requests in time window"""
        try:
            # Get all requests for endpoint
            requests = self.secure_storage.get_requests(endpoint)
            
            # Filter by time window
            return [r for r in requests if r["timestamp"] >= window_start.isoformat()]
        except Exception as e:
            self.logger.error(f"Failed to get requests in window: {str(e)}")
            raise APIError(f"Failed to get requests in window: {str(e)}")
    
    def _initialize_secure_storage(self) -> Any:
        """Initialize secure storage for API keys"""
        try:
            # In production, use HSM-based secure storage
            return {
                "type": "HSM",
                "encryption_key": self.hsm.generate_key_pair()["key_id"],
                "audit_enabled": True
            }
        except Exception as e:
            self.logger.error(f"Secure storage initialization failed: {str(e)}")
            raise APIError(f"Failed to initialize secure storage: {str(e)}")
    
    def _encrypt_api_key(self, key: str) -> str:
        """Encrypt API key using HSM"""
        try:
            # Encrypt with HSM
            encrypted_key = self.hsm.encrypt_data(key.encode())
            return encrypted_key.hex()
        except Exception as e:
            self.logger.error(f"API key encryption failed: {str(e)}")
            raise APIError(f"Failed to encrypt API key: {str(e)}")
    
    def _decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt API key using HSM"""
        try:
            # Decrypt with HSM
            encrypted_bytes = bytes.fromhex(encrypted_key)
            decrypted_key = self.hsm.decrypt_data(encrypted_bytes)
            return decrypted_key.decode()
        except Exception as e:
            self.logger.error(f"API key decryption failed: {str(e)}")
            raise APIError(f"Failed to decrypt API key: {str(e)}")
    
    def generate_secure_api_key(self, user_id: str) -> str:
        """Generate secure API key with HSM"""
        try:
            # Generate secure key
            raw_key = secrets.token_hex(32)
            
            # Encrypt with HSM
            encrypted_key = self._encrypt_api_key(raw_key)
            
            # Store securely
            self.api_keys[user_id] = {
                "key": encrypted_key,
                "created_at": datetime.now().isoformat(),
                "status": "active",
                "encryption_version": "HSM_v1"
            }
            
            # Log secure audit
            self._log_secure_audit(
                "API_KEY_GENERATION",
                {"user_id": user_id, "status": "SUCCESS"}
            )
            
            return raw_key
        except Exception as e:
            self.logger.error(f"Secure API key generation failed: {str(e)}")
            raise APIError(f"Failed to generate secure API key: {str(e)}")
    
    def _log_secure_audit(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log secure audit trail with HSM"""
        try:
            # Create audit record
            audit_data = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "data": data
            }
            
            # Encrypt with HSM
            encrypted_audit = self.hsm.encrypt_data(
                json.dumps(audit_data).encode()
            )
            
            # Store in secure audit log
            self._store_secure_audit(encrypted_audit)
            
            self.logger.info(f"Secure audit log created for {event_type}")
        except Exception as e:
            self.logger.error(f"Audit logging failed: {str(e)}")
            raise APIError(f"Failed to create audit log: {str(e)}")
    
    def _store_secure_audit(self, encrypted_audit: bytes) -> None:
        """Store encrypted audit log securely"""
        try:
            # Store in HSM-based audit storage
            self.hsm._store_key_in_hsm(encrypted_audit)
        except Exception as e:
            self.logger.error(f"Audit storage failed: {str(e)}")
            raise APIError(f"Failed to store audit log: {str(e)}")
    
    def authenticate_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate API request with strict security"""
        try:
            # Get endpoint information
            endpoint = request.get("path", "")
            method = request.get("method", "").upper()
            
            # Validate endpoint
            if endpoint not in self.endpoint_security:
                raise APIError("Invalid endpoint")
            
            # Check method
            if method not in self.endpoint_security[endpoint]["methods"]:
                raise APIError("Method not allowed")
            
            # Get authentication type
            auth_type = self.endpoint_security[endpoint]["authentication"]
            
            # Perform authentication
            if auth_type == "basic":
                self._validate_basic_auth(request)
            elif auth_type == "jwt":
                self._validate_jwt_auth(request)
            
            # Check rate limits
            if self.endpoint_security[endpoint]["rate_limit"]:
                self._check_rate_limit(request)
            
            # Check authorization
            self._check_authorization(request, endpoint)
            
            # Encrypt request if required
            if self.endpoint_security[endpoint]["encryption"]:
                self._encrypt_request(request)
            
            # Log secure audit
            self._log_secure_audit(
                "API_REQUEST",
                {
                    "endpoint": endpoint,
                    "method": method,
                    "status": "SUCCESS"
                }
            )
            
            return request
        except APIError as e:
            self.logger.error(f"API authentication failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"API security error: {str(e)}")
            raise APIError(f"API security error: {str(e)}")
    
    def _encrypt_request(self, request: Dict[str, Any]) -> None:
        """Encrypt request data with HSM"""
        try:
            # Get encryption key from HSM
            encryption_key = self.hsm.generate_key_pair()["key_id"]
            
            # Encrypt request data
            encrypted_data = self.hsm.encrypt_data(
                json.dumps(request).encode()
            )
            
            # Replace request data with encrypted version
            request["encrypted_data"] = encrypted_data.hex()
            request["encryption_key_id"] = encryption_key
            
            self.logger.info("Request data encrypted successfully")
        except Exception as e:
            self.logger.error(f"Request encryption failed: {str(e)}")
            raise APIError(f"Failed to encrypt request data: {str(e)}")
    
    def authenticate_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate API request with strict security"""
        try:
            # Get endpoint information
            endpoint = request.get("path", "")
            method = request.get("method", "").upper()
            
            # Validate endpoint
            if endpoint not in self.endpoint_security:
                raise APIError("Invalid endpoint")
            
            # Check method
            if method not in self.endpoint_security[endpoint]["methods"]:
                raise APIError("Method not allowed")
            
            # Get authentication type
            auth_type = self.endpoint_security[endpoint]["authentication"]
            
            # Perform authentication
            if auth_type == "basic":
                self._validate_basic_auth(request)
            elif auth_type == "jwt":
                self._validate_jwt_auth(request)
            
            # Check rate limits
            if self.endpoint_security[endpoint]["rate_limit"]:
                self._check_rate_limit(request)
            
            # Check authorization
            self._check_authorization(request, endpoint)
            
            return request
        except APIError as e:
            self.logger.error(f"API authentication failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"API security error: {str(e)}")
            raise APIError(f"API security error: {str(e)}")
    
    def _validate_basic_auth(self, request: Dict[str, Any]) -> None:
        """Validate basic authentication"""
        try:
            auth_header = request.get("headers", {}).get("Authorization", "")
            if not auth_header.startswith("Basic "):
                raise APIError("Invalid basic auth header")
            
            # Decode credentials
            credentials = auth_header[6:].encode("utf-8")
            decoded = base64.b64decode(credentials).decode("utf-8")
            username, password = decoded.split(":", 1)
            
            # Validate credentials
            if not self._validate_credentials(username, password):
                raise APIError("Invalid credentials")
        except Exception as e:
            self.logger.error(f"Basic auth validation failed: {str(e)}")
            raise APIError(f"Basic auth validation failed: {str(e)}")
    
    def _validate_jwt_auth(self, request: Dict[str, Any]) -> None:
        """Validate JWT authentication"""
        try:
            auth_header = request.get("headers", {}).get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                raise APIError("Invalid JWT header")
            
            token = auth_header[7:]
            try:
                payload = jwt.decode(
                    token,
                    self.config["jwt_secret"],
                    algorithms=["HS256"]
                )
            except jwt.ExpiredSignatureError:
                raise APIError("Token expired")
            except jwt.InvalidTokenError:
                raise APIError("Invalid token")
            
            # Validate token claims
            if datetime.fromtimestamp(payload["exp"]) < datetime.now():
                raise APIError("Token expired")
            
            request["user_id"] = payload["user_id"]
        except Exception as e:
            self.logger.error(f"JWT validation failed: {str(e)}")
            raise APIError(f"JWT validation failed: {str(e)}")
    
    def _check_rate_limit(self, request: Dict[str, Any]) -> None:
        """Check and enforce rate limits"""
        try:
            client_ip = request.get("client_ip", "")
            endpoint = request.get("path", "")
            
            # Initialize rate limit state
            if client_ip not in self.api_keys:
                self.api_keys[client_ip] = {
                    "requests": 0,
                    "last_reset": datetime.now()
                }
            
            state = self.api_keys[client_ip]
            
            # Reset counter if time window has passed
            if (datetime.now() - state["last_reset"]).total_seconds() > self.rate_limits["time_window_seconds"]:
                state["requests"] = 0
                state["last_reset"] = datetime.now()
            
            # Check request count
            state["requests"] += 1
            if state["requests"] > self.rate_limits["max_requests"]:
                raise APIError("Rate limit exceeded")
        except Exception as e:
            self.logger.error(f"Rate limit check failed: {str(e)}")
            raise APIError(f"Rate limit check failed: {str(e)}")
    
    def _check_authorization(self, request: Dict[str, Any], endpoint: str) -> None:
        """Check user authorization"""
        try:
            user_id = request.get("user_id")
            if not user_id:
                raise APIError("User not authenticated")
            
            # Get user roles
            user_roles = self._get_user_roles(user_id)
            
            # Check required roles
            required_roles = self.endpoint_security[endpoint].get("roles", [])
            if not any(role in user_roles for role in required_roles):
                raise APIError("Unauthorized access")
        except Exception as e:
            self.logger.error(f"Authorization check failed: {str(e)}")
            raise APIError(f"Authorization check failed: {str(e)}")
    
    def _validate_credentials(self, username: str, password: str) -> bool:
        """Validate user credentials"""
        try:
            # In production, this would check against a secure database
            # For simulation, we use a simple check
            return bool(username and password)
        except Exception as e:
            self.logger.error(f"Credential validation failed: {str(e)}")
            raise APIError(f"Credential validation failed: {str(e)}")
    
    def _get_user_roles(self, user_id: str) -> List[str]:
        """Get user roles"""
        try:
            # In production, this would get roles from a secure source
            # For simulation, we return default roles
            return ["admin", "analyst", "reviewer"]
        except Exception as e:
            self.logger.error(f"Role retrieval failed: {str(e)}")
            raise APIError(f"Role retrieval failed: {str(e)}")
    
    def generate_api_key(self, user_id: str) -> str:
        """Generate secure API key"""
        try:
            # Generate secure key
            key = secrets.token_hex(32)
            
            # Store key securely
            self.api_keys[user_id] = {
                "key": key,
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
            
            return key
        except Exception as e:
            self.logger.error(f"API key generation failed: {str(e)}")
            raise APIError(f"API key generation failed: {str(e)}")
    
    def validate_api_key(self, key: str) -> bool:
        """Validate API key"""
        try:
            for user_id, key_info in self.api_keys.items():
                if key_info["key"] == key and key_info["status"] == "active":
                    return True
            return False
        except Exception as e:
            self.logger.error(f"API key validation failed: {str(e)}")
            raise APIError(f"API key validation failed: {str(e)}")
