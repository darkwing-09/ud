"""Auth repository — user CRUD, refresh token management."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UserNotFoundError
from app.db.repositories.base import BaseRepository
from app.models.user import RefreshToken, User


class UserRepository(BaseRepository[User]):
    model = User

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_email(self, email: str, school_id: UUID | None = None) -> User | None:
        stmt = select(User).where(
            and_(
                User.email == email.lower().strip(),
                User.deleted_at.is_(None),
            )
        )
        if school_id is not None:
            stmt = stmt.where(User.school_id == school_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email_or_raise(self, email: str, school_id: UUID | None = None) -> User:
        user = await self.get_by_email(email, school_id)
        if user is None:
            raise UserNotFoundError(f"No user found with email: {email}")
        return user

    async def increment_failed_attempts(self, user: User) -> User:
        user.failed_login_attempts += 1
        self.session.add(user)
        await self.session.flush()
        return user

    async def reset_failed_attempts(self, user: User) -> User:
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.now(timezone.utc)
        self.session.add(user)
        await self.session.flush()
        return user

    async def lock_account(self, user: User, locked_until: datetime) -> User:
        user.locked_until = locked_until
        self.session.add(user)
        await self.session.flush()
        return user

    async def mark_email_verified(self, user: User) -> User:
        user.is_verified = True
        user.is_active = True
        self.session.add(user)
        await self.session.flush()
        return user

    async def update_password(self, user: User, hashed_password: str) -> User:
        user.hashed_password = hashed_password
        self.session.add(user)
        await self.session.flush()
        return user

    async def update_fcm_token(self, user_id: UUID, token: str) -> None:
        await self.session.execute(
            update(User).where(User.id == user_id).values(fcm_token=token)
        )

    async def list_by_school(self, school_id: UUID, role: str | None = None) -> list[User]:
        stmt = select(User).where(
            and_(User.school_id == school_id, User.deleted_at.is_(None))
        )
        if role:
            stmt = stmt.where(User.role == role)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    model = RefreshToken

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    async def create_token(
        self,
        user_id: UUID,
        token: str,
        family_id: str,
        expires_at: datetime,
        user_agent: str | None = None,
        ip_address: str | None = None,
        device_name: str | None = None,
    ) -> RefreshToken:
        return await self.create(
            user_id=user_id,
            token_hash=self.hash_token(token),
            family_id=family_id,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
            device_name=device_name,
        )

    async def get_by_token(self, token: str) -> RefreshToken | None:
        token_hash = self.hash_token(token)
        stmt = select(RefreshToken).where(
            and_(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_by_user(self, user_id: UUID) -> list[RefreshToken]:
        now = datetime.now(timezone.utc)
        stmt = select(RefreshToken).where(
            and_(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > now,
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def revoke_token(self, token: RefreshToken) -> None:
        token.revoked_at = datetime.now(timezone.utc)
        self.session.add(token)
        await self.session.flush()

    async def revoke_all_for_user(self, user_id: UUID) -> int:
        """Revoke all active sessions for a user. Returns count revoked."""
        now = datetime.now(timezone.utc)
        tokens = await self.get_active_by_user(user_id)
        for token in tokens:
            token.revoked_at = now
            self.session.add(token)
        await self.session.flush()
        return len(tokens)

    async def revoke_family(self, family_id: str) -> None:
        """Revoke entire token family (theft detected)."""
        now = datetime.now(timezone.utc)
        stmt = select(RefreshToken).where(
            and_(
                RefreshToken.family_id == family_id,
                RefreshToken.revoked_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        tokens = list(result.scalars().all())
        for token in tokens:
            token.revoked_at = now
            self.session.add(token)
        await self.session.flush()
