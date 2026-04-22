"""Auth API — ALL 16 endpoints, thin handlers, full OpenAPI."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request, status

from app.core.deps import AUTHENTICATED, CurrentUser, DBSession
from app.core.exceptions import BaseAppError
from app.core.rate_limit import auth_rate_limit
from app.schemas.auth import (
    AccessTokenResponse,
    ChangePasswordRequest,
    Disable2FARequest,
    Enable2FAResponse,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    SessionResponse,
    TokenResponse,
    UpdateProfileRequest,
    UserProfileResponse,
    VerifyEmailRequest,
    Verify2FARequest,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["🔐 Authentication"])


# ── Register ──────────────────────────────────────────────────
@router.post(
    "/register",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(auth_rate_limit)],
    summary="Register new user",
    description="Register a new user account. Sends email verification OTP. Admin-seeded accounts only.",
)
async def register(data: RegisterRequest, db: DBSession) -> MessageResponse:
    service = AuthService(db)
    result = await service.register(data)
    return MessageResponse(message=result["message"])


# ── Login ─────────────────────────────────────────────────────
@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(auth_rate_limit)],
    summary="User login",
    description="Authenticate with email + password. Returns JWT access + refresh tokens. 2FA code required if enabled.",
)
async def login(data: LoginRequest, request: Request, db: DBSession) -> TokenResponse:
    service = AuthService(db)
    return await service.login(
        data,
        user_agent=request.headers.get("User-Agent"),
        ip_address=request.client.host if request.client else None,
    )


# ── Refresh Token ─────────────────────────────────────────────
@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Exchange a valid refresh token for a new access token. Implements rotation — old token is invalidated.",
)
async def refresh_token(data: RefreshTokenRequest, db: DBSession) -> AccessTokenResponse:
    service = AuthService(db)
    return await service.refresh(data.refresh_token)


# ── Logout ────────────────────────────────────────────────────
@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout (revoke current session)",
    description="Revoke the current refresh token and blacklist the access token.",
)
async def logout(
    data: LogoutRequest,
    current_user: CurrentUser,
    request: Request,
    db: DBSession,
) -> MessageResponse:
    # Extract JTI from bearer token
    from app.core.security import decode_access_token
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.split(" ", 1)[1] if " " in auth_header else ""
    payload = decode_access_token(token)

    service = AuthService(db)
    await service.logout(data.refresh_token, payload.get("jti", ""))
    return MessageResponse(message="Logged out successfully")


# ── Logout All ────────────────────────────────────────────────
@router.post(
    "/logout-all",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout all sessions",
    description="Revoke all active sessions for the current user. Useful after password change.",
)
async def logout_all(
    current_user: CurrentUser,
    request: Request,
    db: DBSession,
) -> MessageResponse:
    from app.core.security import decode_access_token
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.split(" ", 1)[1] if " " in auth_header else ""
    payload = decode_access_token(token)

    service = AuthService(db)
    count = await service.logout_all(current_user.id, payload.get("jti", ""))
    return MessageResponse(message=f"Logged out from {count} session(s)")


# ── Forgot Password ───────────────────────────────────────────
@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(auth_rate_limit)],
    summary="Request password reset OTP",
    description="Send a password reset OTP to the registered email. Always returns 200 to prevent email enumeration.",
)
async def forgot_password(data: ForgotPasswordRequest, db: DBSession) -> MessageResponse:
    service = AuthService(db)
    await service.forgot_password(data.email)
    return MessageResponse(message="If an account exists, a reset OTP has been sent to your email")


# ── Reset Password ────────────────────────────────────────────
@router.post(
    "/reset-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(auth_rate_limit)],
    summary="Reset password with OTP",
    description="Reset password using the OTP received via email. Token expires in 2 hours.",
)
async def reset_password(data: ResetPasswordRequest, db: DBSession) -> MessageResponse:
    service = AuthService(db)
    await service.reset_password(data.token, data.otp, data.new_password)
    return MessageResponse(message="Password reset successfully. All sessions have been invalidated.")


# ── Change Password ───────────────────────────────────────────
@router.post(
    "/change-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Change password (authenticated)",
    description="Change password for the currently authenticated user. Requires current password.",
)
async def change_password(
    data: ChangePasswordRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> MessageResponse:
    service = AuthService(db)
    await service.change_password(current_user, data.current_password, data.new_password)
    return MessageResponse(message="Password changed successfully. All sessions have been invalidated.")


# ── Verify Email ──────────────────────────────────────────────
@router.post(
    "/verify-email",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify email address",
    description="Verify email using OTP received during registration. Activates the account.",
)
async def verify_email(data: VerifyEmailRequest, db: DBSession) -> MessageResponse:
    service = AuthService(db)
    await service.verify_email(data.token, data.otp)
    return MessageResponse(message="Email verified successfully. You can now log in.")


# ── Me (Get Profile) ──────────────────────────────────────────
@router.get(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Returns complete profile of the authenticated user.",
)
async def get_me(current_user: CurrentUser) -> UserProfileResponse:
    return UserProfileResponse.model_validate(current_user)


# ── Me (Update Profile) ───────────────────────────────────────
@router.patch(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update own profile",
    description="Update name, phone, avatar for the authenticated user.",
)
async def update_me(
    data: UpdateProfileRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> UserProfileResponse:
    service = AuthService(db)
    return await service.update_profile(current_user, data)


# ── 2FA — Enable ──────────────────────────────────────────────
@router.post(
    "/2fa/enable",
    response_model=Enable2FAResponse,
    status_code=status.HTTP_200_OK,
    summary="Enable Two-Factor Authentication (TOTP)",
    description="Generates a TOTP secret and QR code. Complete setup by calling POST /auth/2fa/verify.",
)
async def enable_2fa(current_user: CurrentUser, db: DBSession) -> Enable2FAResponse:
    service = AuthService(db)
    return await service.enable_2fa(current_user)


# ── 2FA — Verify ──────────────────────────────────────────────
@router.post(
    "/2fa/verify",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify and activate 2FA",
    description="Verify TOTP code from authenticator app to confirm 2FA setup.",
)
async def verify_2fa(
    data: Verify2FARequest,
    current_user: CurrentUser,
    db: DBSession,
) -> MessageResponse:
    service = AuthService(db)
    await service.verify_2fa(current_user, data.totp_code)
    return MessageResponse(message="Two-factor authentication enabled successfully")


# ── 2FA — Disable ─────────────────────────────────────────────
@router.post(
    "/2fa/disable",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Disable 2FA",
    description="Disable 2FA by providing current password and a valid TOTP code.",
)
async def disable_2fa(
    data: Disable2FARequest,
    current_user: CurrentUser,
    db: DBSession,
) -> MessageResponse:
    service = AuthService(db)
    await service.disable_2fa(current_user, data.password, data.totp_code)
    return MessageResponse(message="Two-factor authentication disabled")


# ── Sessions — List ───────────────────────────────────────────
@router.get(
    "/sessions",
    response_model=list[SessionResponse],
    status_code=status.HTTP_200_OK,
    summary="List active sessions",
    description="Returns all active login sessions for the current user.",
)
async def list_sessions(current_user: CurrentUser, request: Request, db: DBSession) -> list[SessionResponse]:
    from app.core.security import decode_access_token
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.split(" ", 1)[1] if " " in auth_header else ""
    payload = decode_access_token(token)
    current_jti = payload.get("jti", "")

    service = AuthService(db)
    return await service.get_sessions(current_user.id, current_jti)


# ── Sessions — Revoke Specific ────────────────────────────────
@router.delete(
    "/sessions/{session_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke specific session",
    description="Revoke a specific session by its ID. Use session ID from GET /auth/sessions.",
)
async def revoke_session(
    session_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> MessageResponse:
    service = AuthService(db)
    await service.revoke_session(current_user.id, session_id)
    return MessageResponse(message="Session revoked successfully")
