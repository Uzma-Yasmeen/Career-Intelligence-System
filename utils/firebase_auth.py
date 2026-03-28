import streamlit as st
import requests
import json
import firebase_admin
from firebase_admin import credentials, auth
import os

def init_firebase():
    if not firebase_admin._apps:
        try:
            if 'firebase_key' in st.secrets:
                key_dict = json.loads(st.secrets['firebase_key'])
                cred = credentials.Certificate(key_dict)
            elif os.path.exists('firebase-key.json'):
                cred = credentials.Certificate('firebase-key.json')
            else:
                return False
            firebase_admin.initialize_app(cred)
            return True
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            return False
    return True

def login_user(email, password):
    try:
        api_key = st.secrets.get("firebase_web_api_key", "")
        if not api_key:
            raise Exception("Firebase Web API Key missing")
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        data = {"email": email, "password": password, "returnSecureToken": True}
        r = requests.post(url, json=data)
        if r.status_code == 200:
            user_info = r.json()
            init_firebase() # Ensure Admin SDK is ready
            # Also get user profile for displayName
            try:
                user_record = auth.get_user(user_info['localId'])
                display_name = user_record.display_name or email.split('@')[0]
            except Exception:
                display_name = email.split('@')[0]
            st.session_state['user'] = {
                'uid': user_info['localId'],
                'email': email,
                'displayName': display_name,
                'token': user_info['idToken']
            }
            return True, "Login successful"
        else:
            return False, r.json().get('error', {}).get('message', 'Login failed')
    except Exception as e:
        return False, str(e)

def register_user(email, password, name):
    try:
        api_key = st.secrets.get("firebase_web_api_key", "")
        if not api_key:
            raise Exception("Firebase Web API Key missing")
        
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
        data = {"email": email, "password": password, "returnSecureToken": True}
        r = requests.post(url, json=data)
        if r.status_code == 200:
            user_info = r.json()
            uid = user_info['localId']
            init_firebase() # Ensure Admin SDK is ready
            # update display name using Admin SDK
            try:
                auth.update_user(uid, display_name=name)
            except Exception as e:
                print(f"Admin SDK Update failed: {e}")
            st.session_state['user'] = {
                'uid': uid,
                'email': email,
                'displayName': name,
                'token': user_info['idToken']
            }
            return True, "Registration successful"
        else:
            return False, r.json().get('error', {}).get('message', 'Registration failed')
    except Exception as e:
        return False, str(e)

def is_logged_in():
    return 'user' in st.session_state and st.session_state['user'] is not None

def get_current_user():
    return st.session_state.get('user', None)

def logout():
    if 'user' in st.session_state:
        del st.session_state['user']
