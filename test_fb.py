import toml
import requests

secrets = toml.load(r"c:\Users\Admin\Desktop\Projects\SRU_Projects\ai-career-intelligence\.streamlit\secrets.toml")
api_key = secrets.get("firebase_web_api_key", "")
if not api_key:
    print("API key missing from secrets.toml")
else:
    print("API key found:", api_key[:10] + "...")
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
    data = {"email": "test@example.com", "password": "password123", "returnSecureToken": True}
    r = requests.post(url, json=data)
    print("SignUp Status:", r.status_code)
    print("SignUp Response:", r.json())
