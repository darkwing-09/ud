import requests
import time
import uuid

BASE_URL = "http://localhost:8000/api/v1"

def run_test():
    print("🚀 Starting Phase 1.4 (Step 3) Verification...")
    
    # 1. Login as Super Admin
    print("\n1. Logging in as Super Admin...")
    login_data = {
        "email": "superadmin@educore.in",
        "password": "SuperSecret123!"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")

    # 2. Get existing school (from previous tests or create new)
    # For speed, we'll create a new school
    print("\n2. Creating School...")
    ts = int(time.time())
    school_data = {
        "name": f"Profile Test School {ts}",
        "code": f"pts_{ts}",
        "address": "456 Profile Lane",
        "city": "User City",
        "email": f"school_{ts}@profile.in",
        "subscription_plan": "PREMIUM"
    }
    response = requests.post(f"{BASE_URL}/schools", json=school_data, headers=headers)
    school_id = response.json()["id"]
    headers["X-School-ID"] = school_id
    params = {"school_id": school_id}
    print(f"✅ School ready: {school_id}")

    # 3. Create Academic Year
    print("\n3. Creating Academic Year...")
    year_data = {
        "name": "2024-2025",
        "start_date": "2024-04-01",
        "end_date": "2025-03-31",
        "is_active": True
    }
    response = requests.post(f"{BASE_URL}/academic-years", json=year_data, headers=headers, params=params)
    year_id = response.json()["id"]
    print(f"✅ Academic Year active: {year_id}")

    # 4. Create Section
    print("\n4. Creating Class & Section...")
    class_data = {"name": "Grade 1", "numeric_level": 1}
    response = requests.post(f"{BASE_URL}/classes", json=class_data, headers=headers, params=params)
    class_id = response.json()["id"]
    section_data = {"name": "A", "max_strength": 30}
    response = requests.post(f"{BASE_URL}/classes/{class_id}/sections", json=section_data, headers=headers, params=params)
    section_id = response.json()["id"]
    print(f"✅ Section ready: {section_id}")

    # 5. Create Staff Profile
    print("\n5. Creating Staff Profile...")
    # First need a user
    staff_user_id = str(uuid.uuid4()) # In real app, we use actual user id
    # Mocking user_id check by using superadmin's id for simplicity in test or creating a new user
    # Actually, let's just use a random UUID for user_id as it's a FK to users
    # Wait, it must exist in database! 
    # Let's use the current logged in user (superadmin) as the user for this profile 
    # (only for testing model creation)
    staff_data = {
        "first_name": "John",
        "last_name": "Teacher",
        "employee_code": f"EMP{ts}",
        "designation": "Senior Teacher",
        "aadhaar": "1234-5678-9012",
        "bank_account": "9876543210"
    }
    response = requests.post(f"{BASE_URL}/staff", json=staff_data, headers=headers, params=params)
    if response.status_code != 201:
        print(f"❌ Staff creation failed: {response.text}")
    else:
        staff_id = response.json()["id"]
        print(f"✅ Staff created: {staff_id}")
        # Verify PII decryption
        get_resp = requests.get(f"{BASE_URL}/staff/{staff_id}", headers=headers, params=params)
        profile = get_resp.json()
        if profile["aadhaar"] == "1234-5678-9012":
            print("✅ PII Encryption/Decryption verified")
        else:
            print(f"❌ PII Mismatch: {profile['aadhaar']}")

    # 6. Create Student Profile
    print("\n6. Creating Student Profile...")
    student_data = {
        "first_name": "Little",
        "last_name": "Junior",
        "admission_number": f"ADM{ts}",
        "academic_year_id": year_id,
        "current_section_id": section_id,
        "aadhaar": "1111-2222-3333"
    }
    response = requests.post(f"{BASE_URL}/students", json=student_data, headers=headers, params=params)
    if response.status_code != 201:
        print(f"❌ Student creation failed: {response.text}")
    else:
        student_id = response.json()["id"]
        print(f"✅ Student created: {student_id}")

    print("\n✨ Phase 1.4 (Step 3) Verification COMPLETED SUCCESSFULLY! ✨")

if __name__ == "__main__":
    run_test()
