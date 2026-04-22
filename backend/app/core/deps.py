"""FastAPI dependency injections: DB session, current user, RBAC, rate limiting."""
from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import is_family_blacklisted, is_token_blacklisted
from app.core.config import settings
from app.core.enums import UserRole
from app.models.user import User
from app.core.exceptions import (
    AccountInactiveError,
    AuthenticationError,
    CrossTenantAccessError,
    ForbiddenError,
    InvalidTokenError,
    TokenBlacklistedError,
    TwoFactorRequiredError,
)
from app.core.security import decode_access_token
from app.db.session import get_db

bearer_scheme = HTTPBearer(auto_error=False)


# ── Database ──────────────────────────────────────────────────
DBSession = Annotated[AsyncSession, Depends(get_db)]


# ── Current User ──────────────────────────────────────────────
async def get_current_user_payload(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    request: Request,
) -> dict:
    """Extract and validate JWT payload from Authorization header."""
    if not credentials:
        raise AuthenticationError("Authentication required. Provide Bearer token.")

    token = credentials.credentials
    payload = decode_access_token(token)

    # Check token blacklist
    jti = payload.get("jti", "")
    if await is_token_blacklisted(jti):
        raise TokenBlacklistedError()

    return payload


async def get_current_user(
    db: DBSession,
    payload: Annotated[dict, Depends(get_current_user_payload)],
) -> User:
    """Load the User model from DB using JWT payload."""
    from app.db.repositories.auth import UserRepository
    from app.core.exceptions import UserNotFoundError

    repo = UserRepository(db)
    user_id = UUID(payload["sub"])
    user = await repo.get_by_id(user_id)

    if not user.is_active:
        raise AccountInactiveError()

    # Enforce 2FA on user if enabled
    if user.totp_enabled and not payload.get("2fa_verified"):
        raise TwoFactorRequiredError()

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


# ── School-Scoped Dependencies ────────────────────────────────
async def get_school_id_from_path(
    school_id: UUID,
    current_user: CurrentUser,
) -> UUID:
    """
    Validate that the user is accessing their own school's data.
    SUPER_ADMIN can access any school.
    """
    if current_user.role == UserRole.SUPER_ADMIN.value:
        return school_id
    if current_user.school_id != school_id:
        raise CrossTenantAccessError()
    return school_id


SchoolScopedID = Annotated[UUID, Depends(get_school_id_from_path)]


# ── RBAC Role Guards ──────────────────────────────────────────
def require_roles(*roles: UserRole):
    """Factory: create a dependency that allows only specified roles."""
    async def _role_guard(current_user: CurrentUser) -> User:
        if current_user.role not in roles:
            raise ForbiddenError(
                f"Role {current_user.role} is not permitted. "
                f"Required: {', '.join(r.value for r in roles)}"
            )
        return current_user
    return _role_guard


# ── Convenience Role Dependencies ────────────────────────────
async def require_super_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency for Platform Super Admins only."""
    if current_user.role != UserRole.SUPER_ADMIN.value:
        raise ForbiddenError(f"Platform Super Admin role required. Current: {current_user.role}")
    return current_user

async def require_school_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency for School Admins or Super Admins."""
    allowed = [UserRole.SUPER_ADMIN.value, UserRole.SCHOOL_ADMIN.value]
    if current_user.role not in allowed:
        raise ForbiddenError(f"School Admin role required. Current: {current_user.role}")
    return current_user


SUPER_ADMIN = Annotated[User, Depends(require_roles(UserRole.SUPER_ADMIN))]

SCHOOL_ADMIN = Annotated[
    User,
    Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN)),
]

ADMIN_OR_HR = Annotated[
    User,
    Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN, UserRole.HR_MANAGER)),
]

ADMIN_OR_ACCOUNTANT = Annotated[  # type: ignore[name-defined]
    "User",
    Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN, UserRole.ACCOUNTANT)),
]

TEACHER = Annotated[  # type: ignore[name-defined]
    "User",
    Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN,
        UserRole.CLASS_TEACHER, UserRole.SUBJECT_TEACHER,
    )),
]

ANY_STAFF = Annotated[  # type: ignore[name-defined]
    "User",
    Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN, UserRole.HR_MANAGER,
        UserRole.ACCOUNTANT, UserRole.CLASS_TEACHER, UserRole.SUBJECT_TEACHER,
    )),
]

AUTHENTICATED = Annotated["User", Depends(get_current_user)]  # type: ignore[name-defined]


# ── Rate Limiter ──────────────────────────────────────────────
def get_client_ip(request: Request) -> str:
    """Extract real client IP, considering reverse proxy headers."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"
