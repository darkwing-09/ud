"""AES-256 encryption/decryption for PII fields."""
from __future__ import annotations

import base64
from cryptography.fernet import Fernet
from app.core.config import settings
from app.core.exceptions import BaseAppError

class EncryptionError(BaseAppError):
    """Raised when encryption or decryption fails."""
    status_code = 500
    def __init__(self, detail: str = "Encryption error"):
        super().__init__(detail=detail)

def get_fernet() -> Fernet:
    """Initialize Fernet with the configured key."""
    try:
        key = settings.PII_ENCRYPTION_KEY.strip()
        if not key:
            # Fallback for development
            import hashlib
            key = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode()).digest())
        
        # Ensure it's bytes and valid length
        if isinstance(key, str):
            key = key.encode()
            
        return Fernet(key)
    except Exception as e:
        raise EncryptionError(f"Failed to initialize encryption: {str(e)}")

def encrypt_pii(value: str | None) -> str | None:
    """Encrypt a PII string."""
    if value is None:
        return None
    try:
        f = get_fernet()
        return f.encrypt(value.encode()).decode()
    except Exception as e:
        raise EncryptionError(f"Encryption failed: {str(e)}")

def decrypt_pii(token: str | None) -> str | None:
    """Decrypt an encrypted PII string."""
    if token is None:
        return None
    try:
        f = get_fernet()
        return f.decrypt(token.encode()).decode()
    except Exception as e:
        # If decryption fails (e.g. wrong key or corrupted data), return original or raise?
        # Usually we want to know it failed.
        raise EncryptionError(f"Decryption failed: {str(e)}")
