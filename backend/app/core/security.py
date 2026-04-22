"""Password hashing, JWT token utils, and TOTP helpers."""
from __future__ import annotations

import secrets
import string
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import InvalidTokenError, TokenBlacklistedError

import bcrypt

# ── Password Hashing ──────────────────────────────────────────
def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    # Using encode to prevent bcrypt 72 byte limit bug or truncation issues. 
    # Bcrypt only hashes up to 72 bytes. We can sha256 it first if we want but standard bcrypt is fine.
    # Passlib does some weird detecting that crashes on python 3.12 + bcrypt 4.0.0
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )


def validate_password_strength(password: str) -> list[str]:
    """Validate password meets security requirements. Returns list of errors."""
    errors: list[str] = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters")
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")
    if not any(c in string.punctuation for c in password):
        errors.append("Password must contain at least one special character")
    return errors


# ── JWT Token Creation ────────────────────────────────────────
def create_access_token(
    user_id: UUID,
    school_id: UUID | None,
    role: str,
    additional_claims: dict | None = None,
) -> tuple[str, str]:
    """
    Create JWT access token.
    Returns: (token_string, jti) — jti used for blacklisting
    """
    jti = str(uuid4())
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: dict = {
        "sub": str(user_id),
        "school_id": str(school_id) if school_id else None,
        "role": role,
        "jti": jti,
        "type": "access",
        "iat": now,
        "exp": expire,
    }
    if additional_claims:
        payload.update(additional_claims)

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, jti


def create_refresh_token(user_id: UUID, family_id: str | None = None) -> tuple[str, str, str]:
    """
    Create JWT refresh token with family ID for theft detection.
    Returns: (token_string, jti, family_id)
    """
    jti = str(uuid4())
    fid = family_id or str(uuid4())
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": str(user_id),
        "jti": jti,
        "family_id": fid,
        "type": "refresh",
        "iat": now,
        "exp": expire,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, jti, fid


def create_otp_token(email: str, token_type: str, length: int = 6) -> tuple[str, str]:
    """
    Create short OTP + signed JWT container.
    Returns: (otp_code, signed_token_containing_otp_hash)
    """
    otp = "".join(secrets.choice(string.digits) for _ in range(length))
    now = datetime.now(timezone.utc)

    if token_type == "reset":
        expire_hours = settings.JWT_RESET_TOKEN_EXPIRE_HOURS
    else:
        expire_hours = settings.JWT_VERIFY_TOKEN_EXPIRE_HOURS

    payload = {
        "sub": email,
        "otp": hash_password(otp),  # Store hashed OTP
        "type": token_type,
        "jti": str(uuid4()),
        "iat": now,
        "exp": now + timedelta(hours=expire_hours),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return otp, token


# ── JWT Token Decoding ────────────────────────────────────────
def decode_token(token: str) -> dict:
    """Decode and validate a JWT token. Raises InvalidTokenError on failure."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as exc:
        raise InvalidTokenError(f"Token validation failed: {exc}") from exc


def decode_access_token(token: str) -> dict:
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise InvalidTokenError("Not an access token")
    return payload


def decode_refresh_token(token: str) -> dict:
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise InvalidTokenError("Not a refresh token")
    return payload


def decode_otp_token(token: str, expected_type: str) -> dict:
    payload = decode_token(token)
    if payload.get("type") != expected_type:
        raise InvalidTokenError(f"Expected {expected_type} token")
    return payload


def verify_otp_in_token(otp: str, token: str, token_type: str) -> bool:
    """Verify OTP matches what's stored in the signed token."""
    payload = decode_otp_token(token, token_type)
    stored_hash = payload.get("otp", "")
    return verify_password(otp, stored_hash)


# ── TOTP / 2FA ────────────────────────────────────────────────
def generate_totp_secret() -> str:
    """Generate a base32 TOTP secret for Google Authenticator."""
    import pyotp
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str) -> str:
    """Get TOTP provisioning URI for QR code."""
    import pyotp
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=settings.TOTP_ISSUER_NAME)


def verify_totp(secret: str, otp: str) -> bool:
    """Verify a TOTP OTP against the secret. Allows 1 window drift."""
    import pyotp
    totp = pyotp.TOTP(secret)
    return totp.verify(otp, valid_window=1)


# ── Session Fingerprinting ────────────────────────────────────
def create_session_fingerprint(user_agent: str, ip_address: str) -> str:
    """Create a deterministic fingerprint for a user session."""
    import hashlib
    raw = f"{user_agent}:{ip_address}:{settings.SECRET_KEY}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
