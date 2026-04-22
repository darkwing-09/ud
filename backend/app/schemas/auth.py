"""Auth schemas — Pydantic v2, strict validation, no ORM leakage."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.schemas.common import BaseRequest


class LoginRequest(BaseRequest):

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
    totp_code: str | None = Field(default=None, min_length=6, max_length=6)


class RegisterRequest(BaseRequest):

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=255)

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """Enforce production-grade password complexity."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in v):
            raise ValueError("Password must contain at least one special character")
        return v
    phone: str | None = Field(default=None, pattern=r"^\+?[1-9]\d{9,14}$")
    school_id: UUID | None = None
    role: str = Field(default="STUDENT")

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        if not v.replace(" ", "").isalpha():
            raise ValueError("Full name must contain only letters and spaces")
        return v.title()


class TokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int  # seconds


class AccessTokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    token_type: str = "Bearer"
    expires_in: int


class RefreshTokenRequest(BaseRequest):

    refresh_token: str


class LogoutRequest(BaseRequest):

    refresh_token: str


class ForgotPasswordRequest(BaseRequest):

    email: EmailStr


class ResetPasswordRequest(BaseRequest):

    token: str
    otp: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=8, max_length=128)


class ChangePasswordRequest(BaseRequest):

    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """Enforce production-grade password complexity."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in v):
            raise ValueError("Password must contain at least one special character")
        return v


class VerifyEmailRequest(BaseRequest):

    token: str
    otp: str = Field(min_length=6, max_length=6)


class UpdateProfileRequest(BaseRequest):

    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    phone: str | None = Field(default=None, pattern=r"^\+?[1-9]\d{9,14}$")
    avatar_url: str | None = None


class Enable2FAResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    totp_secret: str
    totp_uri: str
    qr_code_base64: str
    message: str = "Scan the QR code with your authenticator app, then verify with POST /auth/2fa/verify"


class Verify2FARequest(BaseRequest):

    totp_code: str = Field(min_length=6, max_length=6)


class Disable2FARequest(BaseRequest):

    totp_code: str = Field(min_length=6, max_length=6)
    password: str = Field(min_length=1, max_length=128)


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_agent: str | None
    ip_address: str | None
    device_name: str | None
    last_used_at: datetime | None
    created_at: datetime
    is_current: bool = False


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str
    phone: str | None
    avatar_url: str | None
    role: str
    school_id: UUID | None
    is_active: bool
    is_verified: bool
    totp_enabled: bool
    last_login_at: datetime | None
    created_at: datetime


class MessageResponse(BaseModel):
    """Generic success message response."""
    model_config = ConfigDict(from_attributes=True)

    message: str
    success: bool = True
