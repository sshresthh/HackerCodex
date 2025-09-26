from firestore_client import insert_event, get_all_events

# Dummy event to test insertion
dummy_event = {
    "title": "Hackathon Kickoff",
    "category": "Tech",
    "date": "2025-09-26",
    "time": "10:00",
    "location": "Uni Adelaide Hub",
    "source": "Manual",
    "organiser": "CS Club x UPC"
}

# Insert event
insert_event(dummy_event)
print("Inserted one test event!")

# Fetch all events
print("\nAll events in Firestore:")
for e in get_all_events():
    print(e)
