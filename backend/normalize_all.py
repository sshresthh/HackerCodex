import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()


# ========= CONFIG =========
DATA_DIR = os.path.join(os.path.dirname(__file__), "scrapers", "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "normalized_events.json")
OPENCAGE_KEY = os.getenv("OPENCAGE_KEY")  # set this in your .env

# ========= HELPERS =========
def geocode_opencage(address: str):
    """Geocode address using OpenCage API."""
    if not address:
        return {"lat": None, "lng": None}
    try:
        url = "https://api.opencagedata.com/geocode/v1/json"
        params = {"q": f"{address}, South Australia", "key": OPENCAGE_KEY, "limit": 1}
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        if data.get("results"):
            coords = data["results"][0]["geometry"]
            return {"lat": coords["lat"], "lng": coords["lng"]}
    except Exception as e:
        print(f"Geocoding failed for {address}: {e}")
    return {"lat": None, "lng": None}

# ========= NORMALIZERS =========
def normalize_adelaidefestival(raw):
    coords = geocode_opencage(raw.get("address"))
    return {
        "title": raw.get("title"),
        "date": raw.get("date"),
        "time": "TBD",
        "location": None,
        "address": raw.get("address"),
        "lat": coords["lat"],
        "lng": coords["lng"],
        "price": None,
        "description": raw.get("description"),
        "features": [],
        "organiser": "Adelaide Festival Centre",
        "category": "Festival/Arts",
        "source": "AdelaideFestival",
        "link": raw.get("link")
    }

def normalize_eventbrite(raw):
    dt = raw.get("Date & Time", "")
    date, time = None, None
    if "·" in dt:
        parts = dt.split("·")
        date = parts[0].replace("Date and time", "").strip()
        time = parts[1].strip() if len(parts) > 1 else None

    loc = raw.get("Location", "").split("\n")
    location = loc[1] if len(loc) > 1 else None
    address = loc[2] if len(loc) > 2 else None
    coords = geocode_opencage(address)

    return {
        "title": raw.get("Title"),
        "date": date,
        "time": time,
        "location": location,
        "address": address,
        "lat": coords["lat"],
        "lng": coords["lng"],
        "price": None,
        "description": None,
        "features": [],
        "organiser": raw.get("Organizer"),
        "category": raw.get("Category") or "General",
        "source": raw.get("Source") or "Eventbrite",
        "link": raw.get("URL")
    }

def normalize_google(raw):
    addr = ", ".join(raw.get("address", [])) if raw.get("address") else None
    coords = geocode_opencage(addr)
    return {
        "title": raw.get("title"),
        "date": raw.get("date", {}).get("start_date"),
        "time": raw.get("date", {}).get("when"),
        "location": raw.get("address", [None])[0],
        "address": addr,
        "lat": coords["lat"],
        "lng": coords["lng"],
        "price": None,
        "description": raw.get("description"),
        "features": [],
        "organiser": None,
        "category": "General",
        "source": "GoogleEvents",
        "link": raw.get("link")
    }

def normalize_southaustralia(raw):
    coords = geocode_opencage(raw.get("full_address"))
    return {
        "title": raw.get("title"),
        "date": raw.get("dates"),
        "time": "TBD",
        "location": raw.get("location"),
        "address": raw.get("full_address"),
        "lat": coords["lat"],
        "lng": coords["lng"],
        "price": raw.get("price"),
        "description": None,
        "features": raw.get("features", []),
        "organiser": None,
        "category": "Tourism",
        "source": "SouthAustralia",
        "link": raw.get("link")
    }

# ========= LOADER =========
NORMALIZERS = {
    "adelaidefestival.json": normalize_adelaidefestival,
    "eventbrite.json": normalize_eventbrite,
    "google_events.json": normalize_google,
    "southaustralia.json": normalize_southaustralia,
}

def load_and_normalize():
    all_events = []
    for filename, normalizer in NORMALIZERS.items():
        path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(path):
            print(f"Missing file: {filename}")
            continue
        with open(path, "r", encoding="utf-8") as f:
            raw_events = json.load(f)
        for raw in raw_events:
            evt = normalizer(raw)
            all_events.append(evt)
    return all_events

if __name__ == "__main__":
    events = load_and_normalize()
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"Normalized {len(events)} events → {OUTPUT_FILE}")
