"""
Secure AES-256 Encryption System

This module implements secure AES-256 encryption with key management.
"""

import logging
from typing import Tuple, Union
from cryptography.fernet import Fernet
from security.key_management import SecureKeyManager
from config.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class EncryptionError(Exception):
    """Raised when encryption fails"""
    pass

class SecureEncryption:
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize secure encryption system.
        
        Args:
            config: Configuration containing:
                - key_rotation_days: Number of days before key rotation
                - key_size: Size of encryption keys
        """
        self.config = config
        self.config_manager = ConfigManager()
        
        # Initialize key manager
        self.key_manager = SecureKeyManager(config)
        
        # Get encryption key
        self.encryption_key = self.key_manager.generate_encryption_key()
        
        # Initialize Fernet for encryption
        self.fernet = Fernet(base64.urlsafe_b64encode(self.encryption_key))
        
    def encrypt(self, data: Union[str, bytes]) -> Tuple[bytes, bytes]:
        """Encrypt data using secure key management"""
        try:
            if isinstance(data, str):
                data = data.encode()
            
            # Generate session key
            session_key = self.key_manager.generate_session_key()
            
            # Encrypt data using session key
            encrypted_data = self.fernet.encrypt(data)
            
            # Encrypt session key using encryption key
            encrypted_session_key = self.key_manager.encrypt_key(session_key, self.encryption_key)
            
            return encrypted_session_key, encrypted_data
            
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise EncryptionError(f"Encryption failed: {str(e)}")
            
    def decrypt(self, encrypted_session_key: bytes, encrypted_data: bytes) -> bytes:
        """Decrypt data using secure key management"""
        try:
            # Decrypt session key
            session_key = self.key_manager.decrypt_key(encrypted_session_key, self.encryption_key)
            
            # Decrypt data using session key
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise EncryptionError(f"Decryption failed: {str(e)}")
            
    def needs_key_rotation(self) -> bool:
        """Check if key rotation is needed"""
        last_rotation = self.config_manager.get_config("encryption", "last_rotation")
        return self.key_manager.needs_key_rotation(last_rotation)
            
    def rotate_keys(self) -> None:
        """Rotate encryption keys"""
        try:
            # Rotate keys in key manager
            self.key_manager.rotate_keys()
            
            # Get new encryption key
            self.encryption_key = self.key_manager.generate_encryption_key()
            
            # Update Fernet with new key
            self.fernet = Fernet(base64.urlsafe_b64encode(self.encryption_key))
            
            # Update last rotation time
            self.config_manager.set_config("encryption", "last_rotation", datetime.now())
            
            logger.info("Encryption keys successfully rotated")
            
        except Exception as e:
            logger.error(f"Failed to rotate encryption keys: {str(e)}")
            raise EncryptionError("Failed to rotate encryption keys")
    
    def _generate_key(self) -> bytes:
        """Generate secure 256-bit key"""
        return get_random_bytes(32)  # 256 bits
    
    def _pad(self, data: bytes) -> bytes:
        """Pad data to block size"""
        padding = self.block_size - len(data) % self.block_size
        return data + bytes([padding] * padding)
    
    def _unpad(self, data: bytes) -> bytes:
        """Remove padding from data"""
        return data[:-data[-1]]
    
    def encrypt(self, data: Union[str, bytes]) -> Tuple[bytes, bytes]:
        """Encrypt data using AES-256"""
        if isinstance(data, str):
            data = data.encode()
            
        data = self._pad(data)
        iv = get_random_bytes(self.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        
        try:
            encrypted = cipher.encrypt(data)
            return iv, encrypted
        except Exception as e:
            self.logger.error(f"Encryption failed: {str(e)}")
            raise EncryptionError(f"Encryption failed: {str(e)}")
    
    def decrypt(self, iv: bytes, encrypted: bytes) -> bytes:
        """Decrypt data using AES-256"""
        try:
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            decrypted = self._unpad(cipher.decrypt(encrypted))
            return decrypted
        except Exception as e:
            self.logger.error(f"Decryption failed: {str(e)}")
            raise EncryptionError(f"Decryption failed: {str(e)}")
    
    def encrypt_to_base64(self, data: Union[str, bytes]) -> str:
        """Encrypt data and return base64 encoded string"""
        iv, encrypted = self.encrypt(data)
        return base64.b64encode(iv + encrypted).decode()
    
    def decrypt_from_base64(self, data: str) -> str:
        """Decrypt base64 encoded data"""
        data = base64.b64decode(data)
        iv = data[:self.block_size]
        encrypted = data[self.block_size:]
        return self.decrypt(iv, encrypted).decode()
