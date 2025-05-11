"""
Network Security System

This module implements enterprise-grade network security controls.
"""

from typing import Dict, Any, Optional, List
import logging
import socket
import ssl
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from security.hsm import HSM
from security.audit_trail import AuditTrail
from security.traffic_classifier import TrafficClassifier
from security.packet_validator import PacketValidator
from security.ddos_protection import DDoSProtection

logger = logging.getLogger(__name__)

class NetworkSecurityError(Exception):
    """Raised when network security operations fail"""
    pass

class NetworkSecurity:
    """
    Network security controls implementation.
    
    This class implements network security features including:
    - Rate limiting
    - IP whitelisting/blacklisting
    - Request validation
    - Encryption
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize network security controls.
        
        Args:
            config: Configuration containing:
                - rate_limits: Dictionary of rate limits
                - ip_whitelist: List of whitelisted IPs
                - ip_blacklist: List of blacklisted IPs
                - encryption_key: Key for request encryption
        """
        self.config = config
        self.rate_limits = config.get("rate_limits", {})
        self.ip_whitelist = config.get("ip_whitelist", [])
        self.ip_blacklist = config.get("ip_blacklist", [])
        self.encryption_key = config.get("encryption_key")
        self.request_counters = {}
        
        # Security parameters
        self.tls_version = "TLSv1.3"
        self.cipher_suites = config.get("cipher_suites", [
            "TLS_AES_256_GCM_SHA384",
            "TLS_CHACHA20_POLY1305_SHA256",
            "TLS_AES_128_GCM_SHA256"
        ])
        self.traffic_shaping = config.get("traffic_shaping", {
            "max_bandwidth": "100Mbps",
            "priority_levels": 5,
            "queue_size": 1000
        })
        
        # Initialize security components
        self.hsm = HSM(config)
        self.audit = AuditTrail(config)
        self.fernet = Fernet(Fernet.generate_key())
        self.traffic_classifier = TrafficClassifier(config)
        self.packet_validator = PacketValidator(config)
        self.ddos = DDoSProtection(config)
        self.tls_priority = {
            "cipher_suite": "TLS_AES_256_GCM_SHA384",
            "key_exchange": "X25519",
            "signature_algorithm": "Ed25519"
        }
        
        # Initialize network isolation config
        self.network_isolation = {
            "segments": ["DMZ", "INTERNAL", "RESTRICTED"],
            "segments_config": {}
        }
        
        # Initialize security state
        self.connection_state = {}
        self.rate_limit_state = {}
        self.tls_session_cache = {}
        self.packet_fragmentation = {}
        
        # Initialize network isolation
        self._initialize_network_isolation()
        
        # Initialize DDoS protection
        self._initialize_ddos_protection()
    
    def _initialize_network_isolation(self) -> None:
        """Initialize strict network isolation"""
        try:
            # Configure network segments
            for segment in self.network_isolation["segments"]:
                self._configure_segment_rules(segment)
            
            # Enforce HSM-based firewall rules
            self._enforce_firewall_rules()
            
            self.logger.info("Network isolation initialized successfully")
        except Exception as e:
            self.logger.error(f"Network isolation initialization failed: {str(e)}")
            raise NetworkSecurityError(f"Failed to initialize network isolation: {str(e)}")
    
    def _configure_segment_rules(self, segment: str) -> None:
        """Configure security rules for network segment"""
        try:
            # Get segment configuration
            segment_config = self.config.get(f"segment_{segment.lower()}", {})
            
            # Configure HSM-encrypted rules
            rules = self.hsm.encrypt_data(
                json.dumps(segment_config).encode()
            )
            
            # Store in secure segment configuration
            self.network_isolation["segments_config"] = {
                segment: {
                    "rules": rules.hex(),
                    "encryption_key": self.hsm.generate_key_pair()["key_id"]
                }
            }
            
            self.logger.info(f"Segment {segment} rules configured successfully")
        except Exception as e:
            self.logger.error(f"Segment configuration failed: {str(e)}")
            raise NetworkSecurityError(f"Failed to configure segment {segment}: {str(e)}")
    
    def _enforce_firewall_rules(self) -> None:
        """Enforce HSM-based firewall rules"""
        try:
            # Get rules from HSM
            rules = self.hsm.get_firewall_rules()
            
            # Apply rules
            for rule in rules:
                self._apply_firewall_rule(rule)
            
            self.logger.info("Firewall rules enforced successfully")
        except Exception as e:
            self.logger.error(f"Firewall rule enforcement failed: {str(e)}")
            raise NetworkSecurityError(f"Failed to enforce firewall rules: {str(e)}")
    
    def _initialize_ddos_protection(self) -> None:
        """Initialize DDoS protection"""
        try:
            # Configure DDoS protection
            self.ddos.configure(
                max_connections=self.rate_limits["max_requests"],
                time_window=self.rate_limits["time_window_seconds"],
                block_duration=300  # 5 minutes
            )
            
            # Enable HSM-based rate limiting
            self.ddos.enable_hsm_rate_limiting(self.hsm)
            
            self.logger.info("DDoS protection initialized successfully")
        except Exception as e:
            self.logger.error(f"DDoS protection initialization failed: {str(e)}")
            raise NetworkSecurityError(f"Failed to initialize DDoS protection: {str(e)}")
    
    def _handle_packet_fragmentation(self, packet: bytes) -> List[bytes]:
        """Handle secure packet fragmentation"""
        try:
            # Get maximum fragment size from HSM
            max_fragment_size = self.hsm.get_max_fragment_size()
            
            # Fragment packet
            fragments = []
            for i in range(0, len(packet), max_fragment_size):
                fragment = packet[i:i + max_fragment_size]
                encrypted_fragment = self.hsm.encrypt_data(fragment)
                fragments.append(encrypted_fragment)
            
            return fragments
        except Exception as e:
            self.logger.error(f"Packet fragmentation failed: {str(e)}")
            raise NetworkSecurityError(f"Failed to fragment packet: {str(e)}")
    
    def validate_network_access(self, request: Dict[str, Any]) -> bool:
        """Validate network access with comprehensive security"""
        try:
            # Initialize TLS first
            self._initialize_tls()
            
            # Check DDoS protection
            if not self.ddos.check_request(request):
                raise NetworkSecurityError("DDoS protection triggered")
            
            # Validate TLS connection
            if not self._validate_tls(request):
                raise NetworkSecurityError("TLS validation failed")
            
            # Get client information
            client_ip = request.get("client_ip", "")
            client_port = request.get("client_port", 0)
            
            # Check network isolation
            if not self._check_network_isolation(client_ip):
                raise NetworkSecurityError("Network isolation violation")
            
            # IP address validation
            if not self._validate_ip(client_ip):
                raise NetworkSecurityError("Invalid IP address")
            
            # IP whitelist/blacklist check
            if not self._check_ip_policy(client_ip):
                raise NetworkSecurityError("IP access denied")
            
            # Rate limiting
            if not self._check_rate_limit(client_ip):
                raise NetworkSecurityError("Rate limit exceeded")
            
            # Protocol validation
            if not self._validate_protocol(request):
                raise NetworkSecurityError("Invalid protocol")
            
            # Packet inspection
            if not self._inspect_packet(request):
                raise NetworkSecurityError("Malformed packet")
            
            # Connection state validation
            if not self._validate_connection_state(client_ip, client_port):
                raise NetworkSecurityError("Invalid connection state")
            
            # Log secure audit trail
            self._log_secure_audit(request)
            
            return True
        except NetworkSecurityError as e:
            self.logger.error(f"Network access denied: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Network security error: {str(e)}")
            raise NetworkSecurityError(f"Network security error: {str(e)}")
    
    def _check_network_isolation(self, client_ip: str) -> bool:
        """Check network isolation rules"""
        try:
            # Get client segment
            segment = self._get_client_segment(client_ip)
            
            # Check segment rules
            if not self._validate_segment_rules(segment, client_ip):
                return False
            
            # Check cross-segment access
            if not self._validate_cross_segment_access(segment):
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Network isolation check failed: {str(e)}")
            raise NetworkSecurityError(f"Failed to check network isolation: {str(e)}")
    
    def _get_client_segment(self, client_ip: str) -> str:
        """Determine client's network segment"""
        try:
            # Use HSM to determine segment
            return self.hsm.determine_segment(client_ip)
        except Exception as e:
            self.logger.error(f"Segment determination failed: {str(e)}")
            raise NetworkSecurityError(f"Failed to determine segment: {str(e)}")
    
    def _validate_segment_rules(self, segment: str, client_ip: str) -> bool:
        """Validate segment-specific rules"""
        try:
            # Get segment rules from HSM
            rules = self.hsm.get_segment_rules(segment)
            
            # Validate against rules
            return self._check_rules_against_ip(rules, client_ip)
        except Exception as e:
            self.logger.error(f"Segment rules validation failed: {str(e)}")
            raise NetworkSecurityError(f"Failed to validate segment rules: {str(e)}")
    
    def _validate_cross_segment_access(self, segment: str) -> bool:
        """Validate cross-segment access rules"""
        try:
            # Get cross-segment rules from HSM
            rules = self.hsm.get_cross_segment_rules()
            
            # Validate against current segment
            return self._check_cross_segment_rules(rules, segment)
        except Exception as e:
            self.logger.error(f"Cross-segment validation failed: {str(e)}")
            raise NetworkSecurityError(f"Failed to validate cross-segment access: {str(e)}")
    
    def _initialize_tls(self) -> None:
        """Initialize strict TLS 1.3 configuration"""
        try:
            # Generate TLS keys using HSM
            tls_keys = self.hsm.generate_key_pair()
            
            # Configure TLS parameters
            self.tls_config = {
                "version": self.tls_version,
                "cipher_suites": self.tls_cipher_suites,
                "key_exchange": "X25519",
                "signature_algorithm": "Ed25519",
                "key_id": tls_keys["key_id"]
            }
            
            self.logger.info("TLS 1.3 initialized with strict security")
        except Exception as e:
            self.logger.error(f"TLS initialization failed: {str(e)}")
            raise NetworkSecurityError(f"Failed to initialize TLS: {str(e)}")
    
    def _validate_tls(self, request: Dict[str, Any]) -> bool:
        """Validate TLS connection with strict requirements"""
        try:
            # Check TLS version
            if request.get("tls_version") != self.tls_version:
                raise NetworkSecurityError("TLS version not supported")
            
            # Check cipher suite
            if request.get("cipher_suite") not in self.tls_cipher_suites:
                raise NetworkSecurityError("Cipher suite not supported")
            
            # Validate TLS session
            session_id = request.get("tls_session_id")
            if session_id not in self.tls_session_cache:
                # Perform full TLS handshake
                self._perform_tls_handshake(request)
            
            return True
        except NetworkSecurityError as e:
            self.logger.error(f"TLS validation failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"TLS error: {str(e)}")
            raise NetworkSecurityError(f"TLS error: {str(e)}")
    
    def _perform_tls_handshake(self, request: Dict[str, Any]) -> None:
        """Perform strict TLS 1.3 handshake"""
        try:
            # Generate ephemeral key pair
            ephemeral_key = x25519.X25519PrivateKey.generate()
            
            # Perform key exchange with HSM
            shared_secret = self.hsm.perform_key_exchange(
                request["client_ip"],
                request["client_port"]
            )
            
            # Generate session keys
            session_keys = self._derive_session_keys(shared_secret)
            
            # Cache session
            session_id = self._generate_session_id()
            self.tls_session_cache[session_id] = {
                "keys": session_keys,
                "expires": datetime.now() + timedelta(hours=1)
            }
            
            request["tls_session_id"] = session_id
            
            self.logger.info("TLS handshake completed successfully")
        except Exception as e:
            self.logger.error(f"TLS handshake failed: {str(e)}")
            raise NetworkSecurityError(f"TLS handshake failed: {str(e)}")
    
    def _derive_session_keys(self, shared_secret: bytes) -> Dict[str, bytes]:
        """Derive session keys with HSM"""
        try:
            # Use HSM for key derivation
            return {
                "client_write_key": self.hsm.encrypt_data(shared_secret[:16]),
                "server_write_key": self.hsm.encrypt_data(shared_secret[16:32]),
                "client_write_iv": self.hsm.encrypt_data(shared_secret[32:48]),
                "server_write_iv": self.hsm.encrypt_data(shared_secret[48:64])
            }
        except Exception as e:
            self.logger.error(f"Key derivation failed: {str(e)}")
            raise NetworkSecurityError(f"Failed to derive session keys: {str(e)}")
    
    def _generate_session_id(self) -> bytes:
        """Generate secure TLS session ID"""
        try:
            # Use HSM for secure random generation
            return self.hsm.generate_key_pair()["key_id"].encode()
        except Exception as e:
            self.logger.error(f"Session ID generation failed: {str(e)}")
            raise NetworkSecurityError(f"Failed to generate session ID: {str(e)}")
    
    def validate_network_access(self, request: Dict[str, Any]) -> bool:
        """Validate network access with strict security checks"""
        try:
            # Initialize TLS first
            self._initialize_tls()
            
            # Validate TLS connection
            if not self._validate_tls(request):
                raise NetworkSecurityError("TLS validation failed")
            
            # Get client information
            client_ip = request.get("client_ip", "")
            client_port = request.get("client_port", 0)
            
            # IP address validation
            if not self._validate_ip(client_ip):
                raise NetworkSecurityError("Invalid IP address")
            
            # IP whitelist/blacklist check
            if not self._check_ip_policy(client_ip):
                raise NetworkSecurityError("IP access denied")
            
            # Rate limiting
            if not self._check_rate_limit(client_ip):
                raise NetworkSecurityError("Rate limit exceeded")
            
            # Protocol validation
            if not self._validate_protocol(request):
                raise NetworkSecurityError("Invalid protocol")
            
            # Packet inspection
            if not self._inspect_packet(request):
                raise NetworkSecurityError("Malformed packet")
            
            # Connection state validation
            if not self._validate_connection_state(client_ip, client_port):
                raise NetworkSecurityError("Invalid connection state")
            
            # Log secure audit trail
            self._log_secure_audit(request)
            
            return True
        except NetworkSecurityError as e:
            self.logger.error(f"Network access denied: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Network security error: {str(e)}")
            raise NetworkSecurityError(f"Network security error: {str(e)}")
    
    def _log_secure_audit(self, request: Dict[str, Any]) -> None:
        """Log secure audit trail with HSM"""
        try:
            # Create audit record
            audit_data = {
                "timestamp": datetime.now().isoformat(),
                "client_ip": request.get("client_ip", ""),
                "tls_session_id": request.get("tls_session_id", ""),
                "status": "SUCCESS"
            }
            
            # Encrypt audit data with HSM
            encrypted_audit = self.hsm.encrypt_data(
                json.dumps(audit_data).encode()
            )
            
            # Store in secure audit log
            self._store_secure_audit(encrypted_audit)
            
            self.logger.info("Secure audit log created successfully")
        except Exception as e:
            self.logger.error(f"Audit logging failed: {str(e)}")
            raise NetworkSecurityError(f"Failed to create audit log: {str(e)}")
    
    def _store_secure_audit(self, encrypted_audit: bytes) -> None:
        """Store encrypted audit log securely"""
        try:
            # In production, use secure audit storage
            # For simulation, we use HSM storage
            self.hsm._store_key_in_hsm(encrypted_audit)
        except Exception as e:
            self.logger.error(f"Audit storage failed: {str(e)}")
            raise NetworkSecurityError(f"Failed to store audit log: {str(e)}")
    
    def validate_network_access(self, request: Dict[str, Any]) -> bool:
        """Validate network access with strict security checks"""
        try:
            # Get client information
            client_ip = request.get("client_ip", "")
            client_port = request.get("client_port", 0)
            
            # IP address validation
            if not self._validate_ip(client_ip):
                raise NetworkSecurityError("Invalid IP address")
            
            # IP whitelist/blacklist check
            if not self._check_ip_policy(client_ip):
                raise NetworkSecurityError("IP access denied")
            
            # Rate limiting
            if not self._check_rate_limit(client_ip):
                raise NetworkSecurityError("Rate limit exceeded")
            
            # Protocol validation
            if not self._validate_protocol(request):
                raise NetworkSecurityError("Invalid protocol")
            
            # Packet inspection
            if not self._inspect_packet(request):
                raise NetworkSecurityError("Malformed packet")
            
            # Connection state validation
            if not self._validate_connection_state(client_ip, client_port):
                raise NetworkSecurityError("Invalid connection state")
            
            return True
        except NetworkSecurityError as e:
            self.logger.error(f"Network access denied: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Network security error: {str(e)}")
            raise NetworkSecurityError(f"Network security error: {str(e)}")
    
    def _validate_ip(self, ip: str) -> bool:
        """Validate IP address format"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    def _check_ip_policy(self, ip: str) -> bool:
        """Check IP against whitelist/blacklist"""
        try:
            # Check blocked IPs
            if ip in self.blocked_ips:
                return False
            
            # Check allowed IPs
            if self.allowed_ips and ip not in self.allowed_ips:
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"IP policy check failed: {str(e)}")
            raise NetworkSecurityError(f"IP policy check failed: {str(e)}")
    
    def _check_rate_limit(self, ip: str) -> bool:
        """Check and enforce rate limits"""
        try:
            current_time = datetime.now()
            
            # Initialize rate limit state
            if ip not in self.rate_limit_state:
                self.rate_limit_state[ip] = {
                    "requests": 0,
                    "last_reset": current_time
                }
            
            state = self.rate_limit_state[ip]
            
            # Reset counter if time window has passed
            if (current_time - state["last_reset"]).total_seconds() > self.rate_limits["time_window_seconds"]:
                state["requests"] = 0
                state["last_reset"] = current_time
            
            # Check request count
            state["requests"] += 1
            if state["requests"] > self.rate_limits["max_requests"]:
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Rate limit check failed: {str(e)}")
            raise NetworkSecurityError(f"Rate limit check failed: {str(e)}")
    
    def _validate_protocol(self, request: Dict[str, Any]) -> bool:
        """Validate network protocol"""
        try:
            protocol = request.get("protocol", "")
            allowed_protocols = ["HTTPS", "TLS"]
            
            if protocol not in allowed_protocols:
                return False
            
            # Validate protocol version
            version = request.get("protocol_version", "")
            if protocol == "TLS" and version != "1.3":
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Protocol validation failed: {str(e)}")
            raise NetworkSecurityError(f"Protocol validation failed: {str(e)}")
    
    def _inspect_packet(self, request: Dict[str, Any]) -> bool:
        """Inspect network packet for security"""
        try:
            # Check packet size
            if len(str(request)) > self.config.get("max_packet_size", 1024):
                return False
            
            # Check for malicious patterns
            malicious_patterns = [
                "DROP TABLE",
                "DELETE FROM",
                "SELECT * FROM",
                "UNION SELECT"
            ]
            
            for pattern in malicious_patterns:
                if pattern in str(request):
                    return False
            
            # Check packet integrity
            if not self._verify_packet_integrity(request):
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Packet inspection failed: {str(e)}")
            raise NetworkSecurityError(f"Packet inspection failed: {str(e)}")
    
    def _verify_packet_integrity(self, request: Dict[str, Any]) -> bool:
        """Verify packet integrity using HMAC"""
        try:
            # Generate HMAC
            message = str(request)
            key = self.config["packet_integrity_key"]
            
            hmac = hashlib.sha256()
            hmac.update(key.encode())
            hmac.update(message.encode())
            
            # Verify HMAC
            if request.get("hmac") != hmac.hexdigest():
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Packet integrity check failed: {str(e)}")
            raise NetworkSecurityError(f"Packet integrity check failed: {str(e)}")
    
    def _validate_connection_state(self, ip: str, port: int) -> bool:
        """Validate connection state"""
        try:
            # Track connection state
            connection_key = f"{ip}:{port}"
            
            if connection_key not in self.connection_state:
                self.connection_state[connection_key] = {
                    "state": "NEW",
                    "last_activity": datetime.now(),
                    "attempts": 0
                }
            
            state = self.connection_state[connection_key]
            
            # Check connection attempts
            if state["attempts"] >= self.config.get("max_connection_attempts", 3):
                return False
            
            # Update state
            state["last_activity"] = datetime.now()
            state["attempts"] += 1
            
            return True
        except Exception as e:
            self.logger.error(f"Connection state check failed: {str(e)}")
            raise NetworkSecurityError(f"Connection state check failed: {str(e)}")
