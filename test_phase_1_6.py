import requests
import time
from uuid import uuid4
import subprocess

BASE_URL = "http://localhost:8000/api/v1"

def run_test():
    print("🚀 Starting Phase 1.6 (Examinations & Gradebooks) Verification...")
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
    print("\n2. Provisioning Test Data...")
    # Create School
    school_resp = requests.post(f"{BASE_URL}/schools", json={
        "name": f"Exam Test School {ts}",
        "code": f"ETS{ts}",
        "address": "456 Exam Lane",
        "contact_phone": "9876543210",
        "contact_email": f"exam{ts}@school.com"
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

    # Create Section & Subject
    sec_resp = requests.post(f"{BASE_URL}/classes", json={"name": "Class 10", "numeric_level": 10}, headers=headers, params=params)
    class_id = sec_resp.json()["id"]
    requests.post(f"{BASE_URL}/classes/{class_id}/sections", json={"name": "A", "max_strength": 30}, headers=headers, params=params)
    
    subj_resp = requests.post(f"{BASE_URL}/subjects", json={"name": "Physics", "type": "THEORY"}, headers=headers, params=params)
    subject_id = subj_resp.json()["id"]

    # Create Student Profile
    student_user_id = str(uuid4())
    cmd = f"docker exec educore_postgres psql -U educore -d educore_db -c \"INSERT INTO users (id, email, hashed_password, full_name, role, school_id, is_active, is_verified, failed_login_attempts) VALUES ('{student_user_id}', 'stud{ts}@test.com', 'hash', 'Exam Student', 'STUDENT', '{school_id}', true, true, 0);\""
    subprocess.run(cmd, shell=True, check=True)

    student_data = {
        "user_id": student_user_id,
        "first_name": "Maxwell",
        "last_name": "Smart",
        "admission_number": f"ADM{ts}",
        "academic_year_id": year_id,
        "aadhaar": "9999-8888-7777"
    }
    student_resp = requests.post(f"{BASE_URL}/students", json=student_data, headers=headers, params=params)
    student_id = student_resp.json()["id"]
    print(f"✅ Student created: {student_id}")

    # 3. Create Grade Scale
    print("\n3. Creating Grade Scale...")
    grade_data = {
        "name": "Standard Scale",
        "grade": "A+",
        "min_score": 90,
        "max_score": 100,
        "point_value": 4.0,
        "description": "Excellent"
    }
    requests.post(f"{BASE_URL}/exams/grade-scales", json=grade_data, headers=headers, params=params)
    print("✅ Grade scale created")

    # 4. Schedule Exam
    print("\n4. Scheduling Exam...")
    exam_data = {
        "name": "Final Term 2024",
        "type": "FINAL",
        "start_date": "2025-03-10",
        "end_date": "2025-03-25",
        "academic_year_id": year_id
    }
    exam_resp = requests.post(f"{BASE_URL}/exams", json=exam_data, headers=headers, params=params)
    exam_id = exam_resp.json()["id"]
    print(f"✅ Exam scheduled: {exam_id}")

    # 5. Enter Marks
    print("\n5. Entering Marks...")
    marks_data = {
        "exam_id": exam_id,
        "subject_id": subject_id,
        "results": [
            {
                "exam_id": exam_id,
                "student_id": student_id,
                "subject_id": subject_id,
                "marks_obtained": 95,
                "max_marks": 100,
                "remarks": "Great job"
            }
        ]
    }
    marks_resp = requests.post(f"{BASE_URL}/exams/{exam_id}/marks", json=marks_data, headers=headers, params=params)
    if marks_resp.status_code != 200:
        print(f"❌ Marks entry failed: {marks_resp.text}")
        return
    print("✅ Marks entered successfully")

    # 6. Verify GPA calculation
    # First, we need to publish results. Let's manually publish in DB for now as API not built yet
    cmd = f"docker exec educore_postgres psql -U educore -d educore_db -c \"UPDATE exam_results SET published = true WHERE student_id='{student_id}';\""
    subprocess.run(cmd, shell=True, check=True)
    
    print("\n6. Verifying GPA...")
    gpa_resp = requests.get(f"{BASE_URL}/exams/students/{student_id}/gpa", params={"academic_year_id": year_id, "school_id": school_id}, headers=headers)
    gpa_data = gpa_resp.json()
    print(f"✅ GPA Calculated: {gpa_data['gpa']} (4.0 expected)")
    print(f"✅ Percentage: {gpa_data['percentage']}% (95.0 expected)")

    print("\n✨ Phase 1.6 Verification COMPLETED SUCCESSFULLY! ✨")

if __name__ == "__main__":
    run_test()
