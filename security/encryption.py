"""
AES-256 Encryption System

This module implements AES-256 encryption for data protection.
"""

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import base64
import logging
from typing import Tuple, Union

class EncryptionError(Exception):
    """Raised when encryption fails"""
    pass

class AES256Encryption:
    def __init__(self, key: bytes = None):
        self.key = key or self._generate_key()
        self.logger = logging.getLogger(__name__)
        self.block_size = AES.block_size
    
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
