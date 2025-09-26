import firebase_admin
from firebase_admin import credentials, firestore

# Initialize only once
cred = credentials.Certificate("backend/db/serviceAccount.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def insert_event(event: dict):
    """Insert one normalized event into Firestore"""
    db.collection("events").add(event)

def get_all_events():
    """Fetch all events from Firestore"""
    return [doc.to_dict() for doc in db.collection("events").stream()]
