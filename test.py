import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def run_test():
    print("Testing File Upload to FastAPI...")
    
    # 1. Register or Login to get token
    print("Registering a test user...")
    register_response = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": "testuser@example.com",
        "password": "password123",
        "full_name": "Test User"
    })
    
    token = None
    if register_response.status_code == 200:
        token = register_response.json()["access_token"]
        print("Registration successful!")
    elif register_response.status_code == 400: # Already registered
        print("User already exists, logging in...")
        login_response = requests.post(f"{BASE_URL}/api/auth/login", data={
            "username": "testuser@example.com",
            "password": "password123"
        })
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            print("Login successful!")
        else:
            print(f"Login failed: {login_response.text}")
    else:
        print(f"Auth failed: {register_response.text}")
    
    if not token:
        print("Failed to get token! Exiting.")
        return
        
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # 2. Test uploading the existing emails.txt file
    print("\n--- Testing TXT File Upload ---")
    try:
        with open('emails.txt', 'rb') as f:
            files_txt = {'file': ('emails.txt', f, 'text/plain')}
            response_txt = requests.post(f"{BASE_URL}/api/upload-verify", files=files_txt, headers=headers)
        
        if response_txt.status_code == 200:
            print(f"TXT Upload Success! Processed {response_txt.json()['total']} emails.")
            print("Check initial emails output snippet:")
            print(json.dumps(response_txt.json()["results"][:2], indent=2))
        else:
            print(f"TXT Upload Failed: {response_txt.text}")
    except FileNotFoundError:
        print("Could not find emails.txt for testing.")

    # 3. Create and Test uploading a JSON file
    test_json_data = ["test1@gmail.com", "fake_abc123@mailinator.com", "admin@google.com"]
    with open("test_upload.json", "w") as f:
        json.dump(test_json_data, f)
        
    print("\n--- Testing JSON File Upload ---")
    with open('test_upload.json', 'rb') as f:
        files_json = {'file': ('test_upload.json', f, 'application/json')}
        response_json = requests.post(f"{BASE_URL}/api/upload-verify", files=files_json, headers=headers)

    if response_json.status_code == 200:
        print(f"JSON Upload Success! Processed {response_json.json()['total']} emails.")
        print("Full JSON test results:")
        print(json.dumps(response_json.json()["results"], indent=2))
    else:
        print(f"JSON Upload Failed: {response_json.text}")

if __name__ == "__main__":
    run_test()
