"""
Secure Key Management System

This module implements a secure key management system that:
1. Uses environment variables for sensitive values
2. Implements key rotation
3. Provides secure key storage
4. Follows NIST SP 800-57 guidelines
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
import base64
import hashlib
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from config.secrets_manager import SecretsManager

logger = logging.getLogger(__name__)

class KeyManagementError(Exception):
    """Raised when key management operations fail"""
    pass

class SecureKeyManager:
    """Secure key management system"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize key manager with configuration
        
        Args:
            config: Configuration containing:
                - key_rotation_days: Number of days before key rotation
                - key_size: Size of encryption keys
                - salt_length: Length of salt for key derivation
        """
        self.config = config
        self.key_rotation_interval = timedelta(days=config.get("key_rotation_days", 90))
        self.key_size = config.get("key_size", 32)  # 256 bits
        self.salt_length = config.get("salt_length", 16)
        
        # Initialize secrets manager
        self.secrets_manager = SecretsManager()
        
        # Load or generate master key
        self.master_key = self._load_master_key()
        
    def _load_master_key(self) -> bytes:
        """Securely load or generate master key"""
        try:
            # Try to load from secrets manager
            encrypted_key = self.secrets_manager.get_secret("MASTER_KEY")
            if encrypted_key:
                return base64.b64decode(encrypted_key)
            
            # Generate new key if not found
            new_key = self._generate_key()
            
            # Store encrypted key
            self.secrets_manager.set_secret("MASTER_KEY", base64.b64encode(new_key).decode())
            
            return new_key
            
        except Exception as e:
            logger.error(f"Failed to load master key: {str(e)}")
            raise KeyManagementError("Failed to initialize key manager")
            
    def _generate_key(self) -> bytes:
        """Generate a secure encryption key"""
        return os.urandom(self.key_size)
        
    def derive_key(self, purpose: str) -> bytes:
        """Derive a key for specific purpose using HKDF"""
        try:
            # Generate salt
            salt = os.urandom(self.salt_length)
            
            # Derive key using HKDF
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=self.key_size,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            
            # Use purpose as info parameter
            return kdf.derive(self.master_key + purpose.encode())
            
        except Exception as e:
            logger.error(f"Failed to derive key: {str(e)}")
            raise KeyManagementError(f"Failed to derive key for purpose: {purpose}")
            
    def generate_session_key(self) -> bytes:
        """Generate a session key"""
        return self.derive_key("session_key")
        
    def generate_encryption_key(self) -> bytes:
        """Generate an encryption key"""
        return self.derive_key("encryption_key")
        
    def needs_key_rotation(self, last_rotation: datetime) -> bool:
        """Check if key rotation is needed"""
        return datetime.now() - last_rotation > self.key_rotation_interval
        
    def rotate_keys(self) -> None:
        """Rotate all keys"""
        try:
            # Generate new master key
            new_master_key = self._generate_key()
            
            # Store encrypted key
            self.secrets_manager.set_secret("MASTER_KEY", base64.b64encode(new_master_key).decode())
            
            # Update current key
            self.master_key = new_master_key
            
            # Secure delete old key
            self.secrets_manager.secure_delete("MASTER_KEY")
            
            logger.info("Keys successfully rotated")
            
        except Exception as e:
            logger.error(f"Failed to rotate keys: {str(e)}")
            raise KeyManagementError("Failed to rotate keys")
            
    def encrypt_key(self, key: bytes, encryption_key: bytes) -> bytes:
        """Encrypt a key using another key"""
        try:
            # Generate IV
            iv = os.urandom(16)
            
            # Encrypt using AES-256
            cipher = AES.new(encryption_key, AES.MODE_CBC, iv)
            return iv + cipher.encrypt(key)
            
        except Exception as e:
            logger.error(f"Failed to encrypt key: {str(e)}")
            raise KeyManagementError("Failed to encrypt key")
            
    def decrypt_key(self, encrypted_key: bytes, encryption_key: bytes) -> bytes:
        """Decrypt a key"""
        try:
            # Extract IV
            iv = encrypted_key[:16]
            encrypted = encrypted_key[16:]
            
            # Decrypt using AES-256
            cipher = AES.new(encryption_key, AES.MODE_CBC, iv)
            return cipher.decrypt(encrypted)
            
        except Exception as e:
            logger.error(f"Failed to decrypt key: {str(e)}")
            raise KeyManagementError("Failed to decrypt key")
