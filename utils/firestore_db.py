import firebase_admin
from firebase_admin import firestore
import datetime
from .firebase_auth import init_firebase

def get_db():
    if not firebase_admin._apps:
        init_firebase()
    return firestore.client()

def save_analysis(user_id, data):
    db = get_db()
    data['timestamp'] = datetime.datetime.utcnow()
    db.collection('users').document(user_id).collection('analyses').add(data)

def get_user_analyses(user_id):
    db = get_db()
    docs = db.collection('users').document(user_id).collection('analyses').order_by('timestamp', direction=firestore.Query.DESCENDING).get()
    return [doc.to_dict() for doc in docs]

def get_all_analyses():
    db = get_db()
    users_ref = db.collection('users')
    all_analyses = []
    
    # We query all users, then fetch their analyses
    for user_doc in users_ref.stream():
        uid = user_doc.id
        analyses = db.collection('users').document(uid).collection('analyses').get()
        for doc in analyses:
            data = doc.to_dict()
            data['uid'] = uid
            all_analyses.append(data)
            
    return sorted(all_analyses, key=lambda x: x.get('timestamp', ''), reverse=True)
