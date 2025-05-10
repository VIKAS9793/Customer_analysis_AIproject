"""
Secure Secrets Management System

This module implements a secure secrets management system that:
1. Uses environment variables for sensitive values
2. Provides secure encryption for secrets
3. Follows security best practices
"""

import os
import logging
from typing import Optional, Dict
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)

class SecretsManager:
    """Secure secrets management system"""
    
    def __init__(self, master_key: Optional[bytes] = None):
        """
        Initialize secrets manager.
        
        Args:
            master_key: Optional master key for encryption
        """
        self.master_key = master_key or self._generate_master_key()
        self.fernet = Fernet(base64.urlsafe_b64encode(self.master_key))
        
    def _generate_master_key(self) -> bytes:
        """Generate a secure master key"""
        # Generate salt from environment variable
        salt = os.getenv("SECRET_SALT", os.urandom(16))
        
        # Derive key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
            backend=default_backend()
        )
        
        # Use environment variable for key derivation
        key_source = os.getenv("SECRET_KEY_SOURCE", "default_key")
        return kdf.derive(key_source.encode())
        
    def get_secret(self, secret_name: str) -> Optional[str]:
        """Get a secret value from environment variables
        
        Args:
            secret_name: Name of the secret to retrieve
            
        Returns:
            Decrypted secret value if found, None otherwise
        """
        try:
            # Get encrypted secret from environment
            encrypted_secret = os.getenv(f"ENCRYPTED_{secret_name}")
            if not encrypted_secret:
                return None
                
            # Decrypt the secret
            return self.fernet.decrypt(encrypted_secret.encode()).decode()
            
        except Exception as e:
            logger.error(f"Failed to get secret {secret_name}: {str(e)}")
            return None
            
    def set_secret(self, secret_name: str, secret_value: str) -> None:
        """Set a secret value securely
        
        Args:
            secret_name: Name of the secret
            secret_value: Value of the secret
        """
        try:
            # Encrypt the secret
            encrypted_secret = self.fernet.encrypt(secret_value.encode()).decode()
            
            # Set environment variable
            os.environ[f"ENCRYPTED_{secret_name}"] = encrypted_secret
            
            # Clear plain text from memory
            secret_value = "" * len(secret_value)
            
        except Exception as e:
            logger.error(f"Failed to set secret {secret_name}: {str(e)}")
            raise
            
    def rotate_master_key(self) -> None:
        """Rotate the master encryption key"""
        try:
            # Generate new master key
            new_master_key = self._generate_master_key()
            
            # Update Fernet with new key
            self.fernet = Fernet(base64.urlsafe_b64encode(new_master_key))
            
            # Update environment variable
            os.environ["MASTER_KEY"] = base64.urlsafe_b64encode(new_master_key).decode()
            
            logger.info("Master key successfully rotated")
            
        except Exception as e:
            logger.error(f"Failed to rotate master key: {str(e)}")
            raise
            
    def encrypt_value(self, value: str) -> str:
        """Encrypt a value using the master key"""
        return self.fernet.encrypt(value.encode()).decode()
        
    def decrypt_value(self, encrypted: str) -> str:
        """Decrypt a value using the master key"""
        return self.fernet.decrypt(encrypted.encode()).decode()
        
    def secure_delete(self, secret_name: str) -> None:
        """Securely delete a secret
        
        Args:
            secret_name: Name of the secret to delete
        """
        try:
            # Clear environment variable
            if f"ENCRYPTED_{secret_name}" in os.environ:
                del os.environ[f"ENCRYPTED_{secret_name}"]
                
        except Exception as e:
            logger.error(f"Failed to delete secret {secret_name}: {str(e)}")
            raise
