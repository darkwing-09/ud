import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def run_test():
    print("--- 1. Login as SUPER_ADMIN ---")
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "superadmin@educore.in", "password": "SuperSecret123!"}
    )
    if resp.status_code != 200:
        print("Login failed:", resp.text)
        return
    token = resp.json()
    access_token = token["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    print("Login success!")

    print("\n--- 2. Create/Get School ---")
    ts = int(time.time())
    school_data = {
        "name": f"Academic Test School {ts}",
        "code": f"ats_{ts}",
        "address": "123 Academic St",
        "city": "Logic City",
        "email": f"admin_{ts}@academic.in",
        "subscription_plan": "PREMIUM"
    }
    resp = requests.post(f"{BASE_URL}/schools", json=school_data, headers=headers)
    if resp.status_code not in [200, 201]:
        print("Create school failed:", resp.text)
        return
    school = resp.json()
    school_id = school["id"]
    print(f"School ready: {school_id}")

    print("\n--- 3. Create Academic Year ---")
    year_data = {
        "name": "2024-2025",
        "start_date": "2024-04-01",
        "end_date": "2025-03-31",
        "is_active": False
    }
    # Pass school_id in header since it's school-scoped (per get_school_id_from_path)
    # Actually, the router handles it via SchoolScopedID if it's in the path or header?
    # Let's check the router. 
    # @router.post("", ...) 
    # school_id: SchoolScopedID
    
    # Wait, the SchoolScopedID dependency in our current system usually expects XR-School-ID header 
    # OR it's inferred from path if the path has {school_id}.
    # In academic_year.py, the router is /academic-years and doesn't have {school_id}.
    # So it MUST be in the header 'X-School-ID'.
    
    headers["X-School-ID"] = school_id  # Keep header just in case, but use query param
    params = {"school_id": school_id}
    
    resp = requests.post(f"{BASE_URL}/academic-years", json=year_data, headers=headers, params=params)
    if resp.status_code != 201:
        print("Create year failed:", resp.text)
        return
    year = resp.json()
    year_id = year["id"]
    print(f"Academic Year created: {year['name']} (ID: {year_id})")

    print("\n--- 4. Create Term ---")
    term_data = {
        "name": "First Term",
        "start_date": "2024-04-01",
        "end_date": "2024-09-30"
    }
    resp = requests.post(f"{BASE_URL}/academic-years/{year_id}/terms", json=term_data, headers=headers, params=params)
    if resp.status_code != 201:
        print("Create term failed:", resp.text)
    else:
        print("Term created successfully!")

    print("\n--- 5. Activate Year ---")
    resp = requests.post(f"{BASE_URL}/academic-years/{year_id}/activate", headers=headers, params=params)
    if resp.status_code == 200:
        print("Academic Year activated!")
        print("Active:", resp.json()["is_active"])
    else:
        print("Activation failed:", resp.text)

if __name__ == "__main__":
    run_test()
