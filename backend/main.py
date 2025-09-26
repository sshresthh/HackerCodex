from fastapi import FastAPI
from db.firestore_client import insert_event, get_all_events
from scrapers.eventbrite_scraper import scrape_eventbrite

app = FastAPI()

@app.get("/")
def root():
    return {"message": "MergeMap API is running "}

@app.get("/events")
def list_events():
    return get_all_events()

@app.post("/events/scrape/eventbrite")
def scrape_and_store_eventbrite():
    events = scrape_eventbrite()
    for e in events:
        insert_event(e)
    return {"inserted": len(events)}
