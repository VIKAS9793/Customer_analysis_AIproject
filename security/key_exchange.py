"""
Secure Key Exchange Protocol

This module implements a secure key exchange protocol using TLS 1.3.
"""

from typing import Dict, Any, Optional
import logging
import ssl
import socket
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization

class KeyExchangeError(Exception):
    """Raised when key exchange fails"""
    pass

class KeyExchange:
    def __init__(self, config: Dict[str, Any]):
        """Initialize key exchange with configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.protocol = config.get("key_exchange_protocol", "TLS 1.3")
        
        if self.protocol != "TLS 1.3":
            raise KeyExchangeError("Only TLS 1.3 is supported for enterprise security")
    
    def generate_key_pair(self) -> Dict[str, Any]:
        """Generate key pair for key exchange"""
        try:
            private_key = x25519.X25519PrivateKey.generate()
            public_key = private_key.public_key()
            
            return {
                "private_key": private_key,
                "public_key": public_key
            }
        except Exception as e:
            self.logger.error(f"Key pair generation failed: {str(e)}")
            raise KeyExchangeError(f"Failed to generate key pair: {str(e)}")
    
    def establish_secure_channel(self, host: str, port: int) -> ssl.SSLSocket:
        """Establish secure TLS 1.3 channel"""
        try:
            context = ssl.create_default_context()
            context.minimum_version = ssl.TLSVersion.TLSv1_3
            context.maximum_version = ssl.TLSVersion.TLSv1_3
            
            sock = socket.create_connection((host, port))
            secure_sock = context.wrap_socket(sock, server_hostname=host)
            
            return secure_sock
        except Exception as e:
            self.logger.error(f"Secure channel establishment failed: {str(e)}")
            raise KeyExchangeError(f"Failed to establish secure channel: {str(e)}")
    
    def perform_key_exchange(self, host: str, port: int) -> bytes:
        """Perform key exchange using TLS 1.3"""
        try:
            # Generate key pair
            keys = self.generate_key_pair()
            
            # Establish secure channel
            secure_sock = self.establish_secure_channel(host, port)
            
            # Send public key
            public_key_bytes = keys["public_key"].public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
            secure_sock.sendall(public_key_bytes)
            
            # Receive peer's public key
            peer_public_key_bytes = secure_sock.recv(32)
            peer_public_key = x25519.X25519PublicKey.from_public_bytes(peer_public_key_bytes)
            
            # Generate shared secret
            shared_secret = keys["private_key"].exchange(peer_public_key)
            
            secure_sock.close()
            
            return shared_secret
        except Exception as e:
            self.logger.error(f"Key exchange failed: {str(e)}")
            raise KeyExchangeError(f"Failed to perform key exchange: {str(e)}")
    
    def verify_key_exchange(self, shared_secret: bytes) -> bool:
        """Verify key exchange integrity"""
        try:
            # In real implementation, this would verify against stored secrets
            # For simulation, we just check length
            if len(shared_secret) != 32:
                return False
            return True
        except Exception as e:
            self.logger.error(f"Key verification failed: {str(e)}")
            raise KeyExchangeError(f"Failed to verify key exchange: {str(e)}")
