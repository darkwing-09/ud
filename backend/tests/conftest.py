import asyncio
from collections.abc import AsyncGenerator
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app as fastapi_app
from app.db.session import get_db
from app.core.config import settings
from app.db.base import Base
# Import all models to ensure they are registered with Base metadata
import app.models.school
import app.models.user
import app.models.student
import app.models.academic_year
import app.models.class_
import app.models.department
import app.models.section
import app.models.subject
import app.models.attendance
import app.models.examination
import app.models.fee
import app.models.payment
import app.models.payroll
import app.models.salary
import app.models.leave
import app.models.notice
import app.models.message
import app.models.homework
import app.models.event

# Use a separate test database to avoid clobbering dev data
# This assumes the postgres user has permissions to create/drop databases
# Or we just use a different schema/database name that exists.
TEST_DATABASE_URL = settings.DATABASE_URL + "_test"

from sqlalchemy.pool import NullPool

engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Initialize the test database: create all tables."""
    # Note: In a real CI, we might use asyncpg to CREATE DATABASE ..._test first.
    # For now, we assume the DB allows table creation.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a clean database session for each test."""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an AsyncClient that uses the test database session."""
    def override_get_db():
        yield db_session

    fastapi_app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=fastapi_app, base_url="http://test") as ac:
        yield ac
    fastapi_app.dependency_overrides.clear()

# ── Multi-Tenant Fixtures ───────────────────────────────────────────

@pytest.fixture
def school_a_id() -> UUID:
    return uuid4()

@pytest.fixture
def school_b_id() -> UUID:
    return uuid4()
