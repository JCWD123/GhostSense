import requests
import time
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def test_api():
    print("=== Testing FastAPI Endpoints ===")
    
    # 1. Test Config API
    print("\n1. Testing Config API...")
    try:
        resp = requests.get(f"{BASE_URL}/config/")
        if resp.status_code == 200:
            config = resp.json().get("config", {})
            print(f"[SUCCESS] Config API OK. Got {len(config)} keys.")
        else:
            print(f"[FAILURE] Config API Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"[FAILURE] Config API Error: {e}")

    # 2. Test Task Submission
    print("\n2. Testing Task Submission...")
    task_id = None
    try:
        payload = {"query": "Test Query"}
        resp = requests.post(f"{BASE_URL}/tasks/submit?query=Test Query", json={}) # Query param as per code
        if resp.status_code == 200:
            data = resp.json()
            task_id = data.get("task_id")
            print(f"[SUCCESS] Task Submitted. ID: {task_id}")
        else:
            print(f"[FAILURE] Task Submission Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"[FAILURE] Task Submission Error: {e}")

    if not task_id:
        print("Skipping task status check due to submission failure.")
        return

    # 3. Test Task Status
    print(f"\n3. Checking Status for Task {task_id}...")
    for _ in range(5):
        try:
            resp = requests.get(f"{BASE_URL}/tasks/status/{task_id}")
            if resp.status_code == 200:
                status_data = resp.json()
                status = status_data.get("status")
                print(f"   Current Status: {status}")
                if status in ["SUCCESS", "FAILURE"]:
                    print(f"[SUCCESS] Task Finished with status: {status}")
                    break
            else:
                print(f"[FAILURE] Status Check Failed: {resp.status_code}")
        except Exception as e:
            print(f"[FAILURE] Status Check Error: {e}")
        time.sleep(2)

    # 4. Test Sync API
    print("\n4. Testing Sync API...")
    try:
        resp = requests.get(f"{BASE_URL}/sync/data")
        if resp.status_code == 200:
            data = resp.json()
            print(f"[SUCCESS] Sync API OK. Returned {len(data)} records.")
        else:
            print(f"[FAILURE] Sync API Failed: {resp.status_code}")
    except Exception as e:
        print(f"[FAILURE] Sync API Error: {e}")

if __name__ == "__main__":
    # Wait for services to warm up
    print("Waiting 5s for services to start...")
    time.sleep(5)
    test_api()

