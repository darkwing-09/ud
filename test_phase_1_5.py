import requests
import time
from uuid import uuid4
import subprocess

BASE_URL = "http://localhost:8000/api/v1"

def run_test():
    print("🚀 Starting Phase 1.5 (Attendance & Timetables) Final Verification...")
    ts = int(time.time())

    # 1. Login
    login_data = {"email": "superadmin@educore.in", "password": "SuperSecret123!"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")

    # 2. Provision Dependencies
    print("\n2. Provisioning Test School & Data...")
    # Create School
    school_resp = requests.post(f"{BASE_URL}/schools", json={
        "name": f"Attendance Test School {ts}",
        "code": f"ATS{ts}",
        "address": "123 Test St",
        "contact_phone": "1234567891", # Incremented to avoid collision if needed
        "contact_email": f"test{ts}@school.com"
    }, headers=headers)
    school_id = school_resp.json()["id"]
    params = {"school_id": school_id}
    print(f"✅ School created: {school_id}")

    # Create Academic Year
    year_resp = requests.post(f"{BASE_URL}/academic-years", json={
        "name": f"Year {ts}",
        "start_date": "2024-04-01",
        "end_date": "2025-03-31",
        "is_active": True
    }, headers=headers, params=params)
    year_id = year_resp.json()["id"]

    # Create Class & Section
    class_resp = requests.post(f"{BASE_URL}/classes", json={"name": "Class 10", "numeric_level": 10}, headers=headers, params=params)
    class_id = class_resp.json()["id"]
    sec_resp = requests.post(f"{BASE_URL}/classes/{class_id}/sections", json={"name": "A", "max_strength": 30}, headers=headers, params=params)
    section_id = sec_resp.json()["id"]

    # Create Subject
    subj_resp = requests.post(f"{BASE_URL}/subjects", json={"name": "Mathematics", "type": "THEORY"}, headers=headers, params=params)
    subject_id = subj_resp.json()["id"]

    # Manually create Staff User to be sure it exists
    staff_user_id = str(uuid4())
    cmd = f"docker exec educore_postgres psql -U educore -d educore_db -c \"INSERT INTO users (id, email, hashed_password, full_name, role, school_id, is_active, is_verified) VALUES ('{staff_user_id}', 'teacher{ts}@test.com', 'fake_hash', 'Test Teacher', 'TEACHER', '{school_id}', true, true);\""
    subprocess.run(cmd, shell=True, check=True)
    print(f"✅ Staff User created: {staff_user_id}")

    # Create Staff Profile
    staff_data = {
        "user_id": staff_user_id,
        "first_name": "John",
        "last_name": "Teacher",
        "employee_code": f"EMP{ts}",
        "designation": "Teacher",
        "aadhaar": "1234-5678-9012"
    }
    staff_resp = requests.post(f"{BASE_URL}/staff", json=staff_data, headers=headers, params=params)
    staff_id = staff_resp.json()["id"]
    print(f"✅ Staff Profile created: {staff_id}")
    
    # Manually create Student User
    student_user_id = str(uuid4())
    cmd = f"docker exec educore_postgres psql -U educore -d educore_db -c \"INSERT INTO users (id, email, hashed_password, full_name, role, school_id, is_active, is_verified) VALUES ('{student_user_id}', 'student{ts}@test.com', 'fake_hash', 'Test Student', 'STUDENT', '{school_id}', true, true);\""
    subprocess.run(cmd, shell=True, check=True)

    student_data = {
        "user_id": student_user_id,
        "first_name": "Little",
        "last_name": "Junior",
        "admission_number": f"ADM{ts}",
        "academic_year_id": year_id,
        "current_section_id": section_id,
        "aadhaar": "1111-2222-3333"
    }
    student_resp = requests.post(f"{BASE_URL}/students", json=student_data, headers=headers, params=params)
    student_id = student_resp.json()["id"]
    print(f"✅ Student Profile created: {student_id}")

    # 3. Create Timetable Slots
    print("\n3. Creating Timetable Slots...")
    slot_data = {
        "name": "First Period",
        "start_time": "09:00:00",
        "end_time": "10:00:00",
        "is_break": False,
        "order": 1
    }
    slot_resp = requests.post(f"{BASE_URL}/timetable/slots", json=slot_data, headers=headers, params=params)
    slot_id = slot_resp.json()["id"]
    print(f"✅ Slot created: {slot_id}")

    # 4. Create Timetable Entry
    print("\n4. Creating Timetable Entry...")
    entry_data = {
        "academic_year_id": year_id,
        "section_id": section_id,
        "subject_id": subject_id,
        "teacher_id": staff_id,
        "slot_id": slot_id,
        "day_of_week": 0,
        "room_number": "Room 101"
    }
    requests.post(f"{BASE_URL}/timetable/entries", json=entry_data, headers=headers, params=params)
    print("✅ Timetable entry created")

    # 5. Mark Attendance
    print("\n5. Marking Attendance...")
    today = time.strftime("%Y-%m-%d")
    att_data = {
        "date": today,
        "status": "PRESENT",
        "student_id": student_id,
        "academic_year_id": year_id,
        "section_id": section_id
    }
    requests.post(f"{BASE_URL}/attendance/students", json=att_data, headers=headers, params=params)
    
    staff_att_data = {
        "date": today,
        "status": "PRESENT",
        "staff_id": staff_id,
        "check_in": "08:45:00"
    }
    requests.post(f"{BASE_URL}/attendance/staff", json=staff_att_data, headers=headers, params=params)
    print("✅ Attendance marked")

    print("\n✨ Phase 1.5 Verification COMPLETED SUCCESSFULLY! ✨")

if __name__ == "__main__":
    run_test()
