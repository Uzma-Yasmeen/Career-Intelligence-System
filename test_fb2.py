import json
import requests

key_path = r"c:\Users\Admin\Desktop\Projects\SRU_Projects\ai-career-intelligence\.streamlit\secrets.toml"
with open(key_path, "r", encoding="utf-8") as f:
    content = f.read()

web_api_key = None
for line in content.split('\n'):
    if "firebase_web_api_key" in line and "=" in line:
        web_api_key = line.split("=")[1].strip().strip('"')

with open("test_out.txt", "w") as f:
    f.write(f"Extracted API Key: {web_api_key}\n")

    if web_api_key:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={web_api_key}"
        data = {"email": "test@example.com", "password": "password123", "returnSecureToken": True}
        try:
            r = requests.post(url, json=data)
            f.write(f"Registration response: {r.status_code}\n")
            f.write(f"Response JSON: {json.dumps(r.json())}\n")
            
            # also test login
            login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={web_api_key}"
            data_login = {"email": "test@example.com", "password": "password123", "returnSecureToken": True}
            r2 = requests.post(login_url, json=data_login)
            f.write(f"Login response: {r2.status_code}\n")
            f.write(f"Login JSON: {json.dumps(r2.json())}\n")
        except Exception as e:
            f.write(f"Error: {e}\n")
