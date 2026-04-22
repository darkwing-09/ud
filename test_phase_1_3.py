import requests
import time
import uuid

BASE_URL = "http://localhost:8000/api/v1"

def run_test():
    print("🚀 Starting Phase 1.3 Verification...")
    
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

    # 2. Create/Get School
    print("\n2. Creating School...")
    ts = int(time.time())
    school_data = {
        "name": f"Structure Test School {ts}",
        "code": f"sts_{ts}",
        "address": "123 Academic St",
        "city": "Logic City",
        "email": f"admin_{ts}@academic.in",
        "subscription_plan": "PREMIUM"
    }
    response = requests.post(f"{BASE_URL}/schools", json=school_data, headers=headers)
    if response.status_code not in [200, 201]:
        print(f"❌ School creation failed: {response.text}")
        return
    school = response.json()
    school_id = school["id"]
    headers["X-School-ID"] = school_id
    params = {"school_id": school_id}
    print(f"✅ School ready: {school_id}")

    # 3. Create and Activate Academic Year
    print("\n3. Creating Academic Year...")
    year_data = {
        "name": "2024-2025",
        "start_date": "2024-04-01",
        "end_date": "2025-03-31",
        "is_active": True
    }
    response = requests.post(f"{BASE_URL}/academic-years", json=year_data, headers=headers, params=params)
    if response.status_code != 201:
        print(f"❌ Year creation failed: {response.text}")
        return
    year_id = response.json()["id"]
    print(f"✅ Academic Year created and active (ID: {year_id})")

    # 4. Create Department
    print("\n4. Creating Department...")
    dept_data = {
        "name": "Science Department",
        "description": "Department for all science related subjects"
    }
    response = requests.post(f"{BASE_URL}/departments", headers=headers, params=params, json=dept_data)
    if response.status_code != 201:
        print(f"❌ Department creation failed: {response.text}")
        return
    dept_id = response.json()["id"]
    print(f"✅ Department created: {dept_id}")

    # 5. Create Class
    print("\n5. Creating Class...")
    class_data = {
        "name": "Grade 10",
        "numeric_level": 10,
        "department_id": dept_id
    }
    response = requests.post(f"{BASE_URL}/classes", headers=headers, params=params, json=class_data)
    if response.status_code != 201:
        print(f"❌ Class creation failed: {response.text}")
        return
    class_id = response.json()["id"]
    print(f"✅ Class created: {class_id}")

    # 6. Create Section
    print("\n6. Creating Section...")
    section_data = {
        "name": "Section A",
        "max_strength": 35
    }
    response = requests.post(f"{BASE_URL}/classes/{class_id}/sections", headers=headers, params=params, json=section_data)
    if response.status_code != 201:
        print(f"❌ Section creation failed: {response.text}")
        return
    section_id = response.json()["id"]
    print(f"✅ Section created: {section_id}")

    # 7. Create Subject
    print("\n7. Creating Subject...")
    subject_data = {
        "name": "Mathematics",
        "code": "MATH101",
        "type": "THEORY"
    }
    response = requests.post(f"{BASE_URL}/subjects", headers=headers, params=params, json=subject_data)
    if response.status_code != 201:
        print(f"❌ Subject creation failed: {response.text}")
        return
    subject_id = response.json()["id"]
    print(f"✅ Subject created: {subject_id}")

    # 8. Assign Subject to Class/Section
    print("\n8. Assigning Subject to Section...")
    assign_data = {
        "subject_id": subject_id,
        "section_id": section_id,
        "weekly_periods": 6
    }
    response = requests.post(f"{BASE_URL}/subjects/assignments/{class_id}", headers=headers, params=params, json=assign_data)
    if response.status_code != 201:
        print(f"❌ Assignment failed: {response.text}")
        return
    print("✅ Subject assigned successfully")

    # 9. List All to verify
    print("\n9. Verifying Lists...")
    classes_resp = requests.get(f"{BASE_URL}/classes", headers=headers, params=params)
    print(f"✅ Classes count: {len(classes_resp.json())}")
    
    sections_resp = requests.get(f"{BASE_URL}/classes/{class_id}/sections", headers=headers, params=params)
    print(f"✅ Sections count: {len(sections_resp.json())}")

    print("\n✨ Phase 1.3 Verification COMPLETED SUCCESSFULLY! ✨")

if __name__ == "__main__":
    run_test()
