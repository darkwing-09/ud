import requests
import json
import os

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
    print("Login success, token acquired!")

    headers = {"Authorization": f"Bearer {access_token}"}

    print("\n--- 2. Create School ---")
    import time
    ts = int(time.time())
    school_data = {
        "name": f"Springfield High {ts}",
        "code": f"sf_{ts}",
        "address": "742 Evergreen Terrace",
        "city": "Springfield",
        "email": f"admin_{ts}@springfield.in",
        "subscription_plan": "PREMIUM",
        "settings": {
            "min_attendance_percentage": 80,
            "late_fee_per_day": 20.0
        }
    }
    resp = requests.post(f"{BASE_URL}/schools", json=school_data, headers=headers)
    if resp.status_code != 201:
        print("Create school failed:", resp.text)
        return
        
    school = resp.json()
    school_id = school["id"]
    print(f"School created! ID: {school_id}")
    print(json.dumps(school, indent=2))

    print("\n--- 3. Upload Logo ---")
    # Create a dummy image file
    with open("dummy_logo.png", "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82")

    with open("dummy_logo.png", "rb") as f:
        files = {"file": ("dummy_logo.png", f, "image/png")}
        resp = requests.post(f"{BASE_URL}/schools/{school_id}/logo", headers=headers, files=files)
        
    if resp.status_code != 200:
        print("Upload logo failed:", resp.text)
    else:
        print("Logo uploaded successfully!")
        print(json.dumps(resp.json(), indent=2))

if __name__ == "__main__":
    run_test()
