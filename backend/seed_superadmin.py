import asyncio
from app.core.security import hash_password
from app.db.session import AsyncSessionFactory
from app.models.user import User
from app.models.school import School  # Needed for relationship metadata

async def seed_admin():
    async with AsyncSessionFactory() as session:
        # Check if already exists
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.email == "superadmin@educore.in"))
        user = result.scalar_one_or_none()
        if user:
            print(f"User already exists with id: {user.id}")
            return
            
        user = User(
            email="superadmin@educore.in",
            hashed_password=hash_password("SuperSecret123!"),
            full_name="Platform Admin",
            role="SUPER_ADMIN",
            is_active=True,
            is_verified=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        print(f"Super admin created with id: {user.id}")

if __name__ == "__main__":
    asyncio.run(seed_admin())
