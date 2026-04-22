import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from datetime import datetime, timezone, date

from app.models.school import School
from app.models.user import User
from app.models.student import StudentProfile
from app.models.academic_year import AcademicYear
from app.core.security import create_access_token
from app.core.enums import UserRole

def get_now():
    return datetime.now(timezone.utc)

@pytest.mark.asyncio
async def test_cross_tenant_access_denied(client: AsyncClient, db_session: AsyncSession):
    """
    Test that a School Admin from School A cannot access School B's endpoints.
    """
    s_a_id = uuid4()
    s_b_id = uuid4()
    now = get_now()
    
    school_a = School(id=s_a_id, name=f"School A {s_a_id}", code=f"SCLA_{s_a_id.hex[:6]}", created_at=now, updated_at=now)
    db_session.add(school_a)
    await db_session.flush()
    
    school_b = School(id=s_b_id, name=f"School B {s_b_id}", code=f"SCLB_{s_b_id.hex[:6]}", created_at=now, updated_at=now)
    db_session.add(school_b)
    await db_session.flush()

    admin_a = User(
        school_id=s_a_id,
        email=f"admin_{uuid4().hex}@test.com",
        hashed_password="...", 
        role=UserRole.SCHOOL_ADMIN.value,
        full_name="Admin A",
        is_verified=True,
        is_active=True,
        created_at=now,
        updated_at=now
    )
    db_session.add(admin_a)
    await db_session.commit()
    await db_session.refresh(admin_a)

    token_a, _ = create_access_token(user_id=admin_a.id, school_id=s_a_id, role=admin_a.role)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    response = await client.get(f"/api/v1/students?school_id={s_b_id}", headers=headers_a)

    assert response.status_code == 403
    assert response.json()["error_code"] == "CrossTenantAccessError"


@pytest.mark.asyncio
async def test_tenant_data_isolation_listing(client: AsyncClient, db_session: AsyncSession):
    """
    Test that listing students only returns students belonging to the requester's school.
    """
    s_a_id = uuid4()
    s_b_id = uuid4()
    now = get_now()
    
    school_a = School(id=s_a_id, name=f"School A {s_a_id}", code=f"SCLA_L_{s_a_id.hex[:6]}", created_at=now, updated_at=now)
    db_session.add(school_a)
    await db_session.flush()
    
    school_b = School(id=s_b_id, name=f"School B {s_b_id}", code=f"SCLB_L_{s_b_id.hex[:6]}", created_at=now, updated_at=now)
    db_session.add(school_b)
    await db_session.flush()

    start_date = date(2023, 4, 1)
    end_date = date(2024, 3, 31)

    ay_a = AcademicYear(
        school_id=s_a_id, name=f"AY {uuid4().hex[:6]}", 
        start_date=start_date, end_date=end_date, 
        is_active=True, created_at=now, updated_at=now
    )
    db_session.add(ay_a)
    await db_session.flush()
    
    ay_b = AcademicYear(
        school_id=s_b_id, name=f"AY {uuid4().hex[:6]}", 
        start_date=start_date, end_date=end_date, 
        is_active=True, created_at=now, updated_at=now
    )
    db_session.add(ay_b)
    await db_session.flush()
    
    await db_session.commit()
    await db_session.refresh(ay_a)
    await db_session.refresh(ay_b)

    student_a = StudentProfile(
        school_id=s_a_id, admission_number=f"ADM-A-{uuid4().hex[:4]}", 
        first_name="Alice", last_name="A", academic_year_id=ay_a.id,
        status="ACTIVE", created_at=now, updated_at=now
    )
    db_session.add(student_a)
    await db_session.flush()
    
    student_b = StudentProfile(
        school_id=s_b_id, admission_number=f"ADM-B-{uuid4().hex[:4]}", 
        first_name="Bob", last_name="B", academic_year_id=ay_b.id,
        status="ACTIVE", created_at=now, updated_at=now
    )
    db_session.add(student_b)
    await db_session.flush()
    await db_session.commit()

    admin_a = User(
        school_id=s_a_id,
        email=f"admin_{uuid4().hex}@test.com",
        role=UserRole.SCHOOL_ADMIN.value,
        full_name="List Admin",
        is_verified=True,
        is_active=True,
        hashed_password="...",
        created_at=now,
        updated_at=now
    )
    db_session.add(admin_a)
    await db_session.commit()
    await db_session.refresh(admin_a)

    token_a, _ = create_access_token(user_id=admin_a.id, school_id=s_a_id, role=admin_a.role)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    response = await client.get(f"/api/v1/students?school_id={s_a_id}", headers=headers_a)

    assert response.status_code == 200
    data = response.json()
    admission_numbers = [s["admission_number"] for s in data]
    
    assert student_a.admission_number in admission_numbers
    assert student_b.admission_number not in admission_numbers
    assert len(data) >= 1
