import json
import requests
import sys

key_path = r"c:\Users\Admin\Desktop\Projects\SRU_Projects\ai-career-intelligence\.streamlit\secrets.toml"
try:
    with open(key_path, "r", encoding="utf-8") as f:
        content = f.read()
except Exception as e:
    print(f"Failed to read secrets: {e}")
    sys.exit(1)

web_api_key = None
for line in content.split('\n'):
    if "firebase_web_api_key" in line and "=" in line:
        web_api_key = line.split("=")[1].strip().strip('"').strip("'")

with open("fb_debug.txt", "w") as f:
    if not web_api_key:
        f.write("Error: Could not find firebase_web_api_key in secrets.toml\n")
        sys.exit(1)
        
    f.write(f"Using API Key: {web_api_key}\n")
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={web_api_key}"
    # Use a random email to avoid EMAIL_EXISTS error in case it did work
    import uuid
    test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    data = {"email": test_email, "password": "password123", "returnSecureToken": True}
    
    try:
        r = requests.post(url, json=data)
        f.write(f"Status Code: {r.status_code}\n")
        f.write(f"Response: {json.dumps(r.json(), indent=2)}\n")
    except Exception as e:
        f.write(f"Request Error: {str(e)}\n")
