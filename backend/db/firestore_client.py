import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firestore connection (run once)
cred = credentials.Certificate("backend/db/serviceAccount.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def insert_event(event: dict):
    """Insert one event document into Firestore"""
    db.collection("events").add(event)

def get_all_events():
    """Fetch all events from Firestore"""
    docs = db.collection("events").stream()
    return [doc.to_dict() for doc in docs]
