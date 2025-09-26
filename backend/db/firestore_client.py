import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firestore connection (run once)
cred = credentials.Certificate("backend/db/serviceAccount.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def normalize_event(raw: dict) -> dict:
    """Ensure event dict matches expected format"""
    return {
        "title": raw.get("title", "Untitled"),
        "category": raw.get("category", "General"),
        "date": raw.get("date", "TBD"),
        "time": raw.get("time", "TBD"),
        "location": raw.get("location", "Unknown"),
        "source": raw.get("source", "Unknown"),
        "organiser": raw.get("organiser", "Unknown")
    }

def insert_event(event: dict):
    """Insert one normalized event into Firestore"""
    db.collection("events").add(normalize_event(event))

def get_all_events():
    """Fetch all events from Firestore"""
    docs = db.collection("events").stream()
    return [doc.to_dict() for doc in docs]
