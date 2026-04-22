"""Auth service — all authentication business logic."""
from __future__ import annotations

import base64
import io
from datetime import datetime, timedelta, timezone
from uuid import UUID

import qrcode
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import (
    blacklist_refresh_family,
    blacklist_token,
    is_family_blacklisted,
    is_token_blacklisted,
)
from app.core.config import settings
from app.core.exceptions import (
    AccountLockedError,
    AccountInactiveError,
    EmailAlreadyExistsError,
    EmailNotVerifiedError,
    InvalidCredentialsError,
    InvalidOTPError,
    InvalidTokenError,
    SamePasswordError,
    TokenBlacklistedError,
    TwoFactorRequiredError,
    WeakPasswordError,
)
from app.core.security import (
    create_access_token,
    create_otp_token,
    create_refresh_token,
    decode_refresh_token,
    generate_totp_secret,
    get_totp_uri,
    hash_password,
    validate_password_strength,
    verify_otp_in_token,
    verify_password,
    verify_totp,
)
from app.db.repositories.auth import RefreshTokenRepository, UserRepository
from app.models.user import User
from app.schemas.auth import (
    AccessTokenResponse,
    Disable2FARequest,
    Enable2FAResponse,
    LoginRequest,
    RegisterRequest,
    SessionResponse,
    TokenResponse,
    UpdateProfileRequest,
    UserProfileResponse,
    Verify2FARequest,
)

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.token_repo = RefreshTokenRepository(session)

    # ── Register ──────────────────────────────────────────────
    async def register(self, data: RegisterRequest) -> dict:
        """Register a new user account (invited/seeded by admin)."""
        email = data.email.lower().strip()

        # Check uniqueness within school scope
        existing = await self.user_repo.get_by_email(email, data.school_id)
        if existing is not None:
            raise EmailAlreadyExistsError()

        # Validate password
        errors = validate_password_strength(data.password)
        if errors:
            raise WeakPasswordError("; ".join(errors))

        async with self.session.begin_nested():
            user = await self.user_repo.create(
                email=email,
                hashed_password=hash_password(data.password),
                full_name=data.full_name,
                phone=data.phone,
                school_id=data.school_id,
                role=data.role,
                is_active=False,
                is_verified=False,
            )
            await self.session.commit()

        # Send verification email via Celery
        otp, token = create_otp_token(email, "email_verify")
        from app.workers.tasks.email_tasks import send_email_verification
        send_email_verification.delay(
            user_id=str(user.id),
            email=email,
            full_name=data.full_name,
            otp=otp,
            token=token,
        )

        return {"message": "Account created. Check your email for verification OTP.", "user_id": str(user.id)}

    # ── Login ─────────────────────────────────────────────────
    async def login(
        self,
        data: LoginRequest,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> TokenResponse:
        email = data.email.lower().strip()
        user = await self.user_repo.get_by_email(email)

        # Generic error to prevent email enumeration
        if user is None:
            raise InvalidCredentialsError()

        # Check account lock
        if user.is_locked:
            raise AccountLockedError()

        # Verify password
        if not verify_password(data.password, user.hashed_password):
            await self.user_repo.increment_failed_attempts(user)
            if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS - 1:
                locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                await self.user_repo.lock_account(user, locked_until)
            await self.session.commit()
            raise InvalidCredentialsError()

        if not user.is_active:
            raise AccountInactiveError()

        if not user.is_verified:
            raise EmailNotVerifiedError()

        # 2FA check
        if user.totp_enabled:
            if not data.totp_code:
                raise TwoFactorRequiredError()
            if not verify_totp(user.totp_secret or "", data.totp_code):
                raise InvalidOTPError("Invalid 2FA code")

        # Reset failed attempts and issue tokens in one transaction
        # Reset failed attempts and issue tokens
        await self.user_repo.reset_failed_attempts(user)
        # issue_tokens handles its own commit/flush
        return await self._issue_tokens(user, user_agent, ip_address, in_transaction=False)

    # ── Refresh Token ─────────────────────────────────────────
    async def refresh(self, refresh_token_str: str) -> AccessTokenResponse:
        payload = decode_refresh_token(refresh_token_str)
        jti = payload.get("jti", "")
        family_id = payload.get("family_id", "")
        user_id = UUID(payload["sub"])

        # Check family blacklist (token theft)
        if await is_family_blacklisted(family_id):
            raise TokenBlacklistedError("Session has been invalidated.")

        # Validate token in DB
        db_token = await self.token_repo.get_by_token(refresh_token_str)
        if db_token is None or not db_token.is_active:
            # Token reuse = theft detected — blacklist entire family
            expire_secs = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400
            await blacklist_refresh_family(family_id, expire_secs)
            raise TokenBlacklistedError("Token reuse detected. All sessions invalidated.")

        user = await self.user_repo.get_by_id(user_id)
        if not user.is_active:
            raise AccountInactiveError()

        # Rotate: revoke old, issue new
        async with self.session.begin():
            await self.token_repo.revoke_token(db_token)

        access_token, _ = create_access_token(user.id, user.school_id, user.role)
        return AccessTokenResponse(
            access_token=access_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    # ── Logout ────────────────────────────────────────────────
    async def logout(self, refresh_token_str: str, access_jti: str) -> None:
        db_token = await self.token_repo.get_by_token(refresh_token_str)
        if db_token:
            async with self.session.begin():
                await self.token_repo.revoke_token(db_token)

        # Blacklist access token until its natural expiry
        expire_secs = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        await blacklist_token(access_jti, expire_secs)

    async def logout_all(self, user_id: UUID, access_jti: str) -> int:
        async with self.session.begin():
            count = await self.token_repo.revoke_all_for_user(user_id)

        expire_secs = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        await blacklist_token(access_jti, expire_secs)
        return count

    # ── Password Management ───────────────────────────────────
    async def forgot_password(self, email: str) -> None:
        """Send password reset OTP. Always returns 200 (no email enumeration)."""
        user = await self.user_repo.get_by_email(email.lower().strip())
        if user is None:
            return  # Silently succeed

        otp, token = create_otp_token(email.lower(), "reset")
        from app.workers.tasks.email_tasks import send_password_reset_email
        send_password_reset_email.delay(
            email=email,
            full_name=user.full_name,
            otp=otp,
            token=token,
        )

    async def reset_password(self, token: str, otp: str, new_password: str) -> None:
        if not verify_otp_in_token(otp, token, "reset"):
            raise InvalidOTPError()

        from app.core.security import decode_otp_token
        payload = decode_otp_token(token, "reset")
        email = payload["sub"]

        errors = validate_password_strength(new_password)
        if errors:
            raise WeakPasswordError("; ".join(errors))

        user = await self.user_repo.get_by_email_or_raise(email)
        if verify_password(new_password, user.hashed_password):
            raise SamePasswordError()

        async with self.session.begin():
            await self.user_repo.update_password(user, hash_password(new_password))
            await self.token_repo.revoke_all_for_user(user.id)

    async def change_password(self, user: User, current_password: str, new_password: str) -> None:
        if not verify_password(current_password, user.hashed_password):
            raise InvalidCredentialsError("Current password is incorrect")
        if verify_password(new_password, user.hashed_password):
            raise SamePasswordError()

        errors = validate_password_strength(new_password)
        if errors:
            raise WeakPasswordError("; ".join(errors))

        async with self.session.begin():
            await self.user_repo.update_password(user, hash_password(new_password))
            await self.token_repo.revoke_all_for_user(user.id)

    # ── Email Verification ────────────────────────────────────
    async def verify_email(self, token: str, otp: str) -> None:
        if not verify_otp_in_token(otp, token, "email_verify"):
            raise InvalidOTPError()

        from app.core.security import decode_otp_token
        payload = decode_otp_token(token, "email_verify")
        email = payload["sub"]

        user = await self.user_repo.get_by_email_or_raise(email)
        async with self.session.begin():
            await self.user_repo.mark_email_verified(user)

    # ── 2FA Management ────────────────────────────────────────
    async def enable_2fa(self, user: User) -> Enable2FAResponse:
        secret = generate_totp_secret()
        totp_uri = get_totp_uri(secret, user.email)

        # Generate QR code as base64
        img = qrcode.make(totp_uri)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        qr_b64 = base64.b64encode(buf.getvalue()).decode()

        # Store encrypted secret temporarily (not yet enabled — verify first)
        async with self.session.begin():
            user.totp_secret = secret  # Encrypt in production with PII_ENCRYPTION_KEY
            self.session.add(user)

        return Enable2FAResponse(
            totp_secret=secret,
            totp_uri=totp_uri,
            qr_code_base64=f"data:image/png;base64,{qr_b64}",
        )

    async def verify_2fa(self, user: User, totp_code: str) -> None:
        if not user.totp_secret:
            raise InvalidOTPError("2FA setup not initiated")
        if not verify_totp(user.totp_secret, totp_code):
            raise InvalidOTPError("Invalid authenticator code")

        async with self.session.begin():
            user.totp_enabled = True
            self.session.add(user)

    async def disable_2fa(self, user: User, password: str, totp_code: str) -> None:
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Password is incorrect")
        if not user.totp_secret or not verify_totp(user.totp_secret, totp_code):
            raise InvalidOTPError("Invalid authenticator code")

        async with self.session.begin():
            user.totp_enabled = False
            user.totp_secret = None
            self.session.add(user)

    # ── Sessions ──────────────────────────────────────────────
    async def get_sessions(self, user_id: UUID, current_jti: str) -> list[SessionResponse]:
        tokens = await self.token_repo.get_active_by_user(user_id)
        sessions = []
        for token in tokens:
            sessions.append(SessionResponse(
                id=token.id,
                user_agent=token.user_agent,
                ip_address=token.ip_address,
                device_name=token.device_name,
                last_used_at=token.last_used_at,
                created_at=token.created_at,
            ))
        return sessions

    async def revoke_session(self, user_id: UUID, session_id: UUID) -> None:
        token = await self.token_repo.get_by_id(session_id)
        if token.user_id != user_id:
            from app.core.exceptions import ForbiddenError
            raise ForbiddenError("Cannot revoke another user's session")
        async with self.session.begin():
            await self.token_repo.revoke_token(token)

    # ── Profile ───────────────────────────────────────────────
    async def update_profile(self, user: User, data: UpdateProfileRequest) -> UserProfileResponse:
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        async with self.session.begin():
            await self.user_repo.update(user, **update_data)
        return UserProfileResponse.model_validate(user)

    # ── Internal Helpers ──────────────────────────────────────
    async def _issue_tokens(
        self,
        user: User,
        user_agent: str | None,
        ip_address: str | None,
        in_transaction: bool = False,
    ) -> TokenResponse:
        access_token, _ = create_access_token(user.id, user.school_id, user.role)
        refresh_token_str, _jti, family_id = create_refresh_token(user.id)

        expire_at = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        
        await self.token_repo.create_token(
            user_id=user.id,
            token=refresh_token_str,
            family_id=family_id,
            expires_at=expire_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        await self.session.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
