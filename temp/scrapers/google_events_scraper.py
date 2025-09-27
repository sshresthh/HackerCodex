import os
import json
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()

# save inside backend/scrapers/data/
DATA_PATH = os.path.join(os.path.dirname(
    __file__), "data", "google_events.json")


def scrape_google_events():
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        raise ValueError("Missing SERPAPI_KEY in .env")

    params = {
        "engine": "google_events",
        "q": "events in Adelaide",  # fixed search
        "hl": "en",
        "gl": "au",
        "api_key": api_key,
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    events = []
    for event in results.get("events_results", []):
        events.append({
            "title": event.get("title"),
            "date": event.get("date"),
            "address": event.get("address"),
            "description": event.get("description"),
            "link": event.get("link"),
        })

    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

    print(f"Scraped {len(events)} events from Google Events (Adelaide)")
    return events


if __name__ == "__main__":
    scrape_google_events()
