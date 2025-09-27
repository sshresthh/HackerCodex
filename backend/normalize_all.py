import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# ========= CONFIG =========
DATA_DIR = os.path.join(os.path.dirname(__file__), "scrapers", "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "normalized_events.json")
OPENCAGE_KEY = os.getenv("OPENCAGE_KEY")

# ========= HELPERS =========


def geocode_opencage(address: str):
    """Geocode address using OpenCage API."""
    if not address:
        return {"lat": None, "lng": None}
    try:
        url = "https://api.opencagedata.com/geocode/v1/json"
        params = {"q": f"{address}, South Australia",
                  "key": OPENCAGE_KEY, "limit": 1}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("results"):
            coords = data["results"][0]["geometry"]
            print(
                f"Geocoded: {address[:50]}... -> {coords['lat']:.4f}, {coords['lng']:.4f}")
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
        "link": raw.get("link"),
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
        "link": raw.get("URL"),
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
        "link": raw.get("link"),
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
        "link": raw.get("link"),
    }


def normalize_ticketmaster(raw):
    organizer = raw.get("organizer", "")
    if "|" in organizer:
        organizer = organizer.split("|")[0].strip()

    description = raw.get("description", "")
    if "|" in description and len(description) > 200:
        description = description.split("|")[0].strip()

    organizer = organizer or None
    description = description or None

    address = raw.get("location", "")
    coords = geocode_opencage(address) if address else {
        "lat": None, "lng": None}

    return {
        "title": raw.get("title"),
        "date": raw.get("date"),
        "time": raw.get("time"),
        "location": raw.get("venue"),
        "address": raw.get("location"),
        "lat": coords["lat"],
        "lng": coords["lng"],
        "price": raw.get("price_range") or None,
        "description": description,
        "features": [],
        "organiser": organizer,
        "category": raw.get("category", "Entertainment"),
        "source": "Ticketmaster",
        "link": raw.get("link"),
    }

# ========= LOADER =========


NORMALIZERS = {
    "adelaidefestival.json": normalize_adelaidefestival,
    "eventbrite.json": normalize_eventbrite,
    "google_events.json": normalize_google,
    "southaustralia.json": normalize_southaustralia,
    "ticketmaster.json": normalize_ticketmaster,
}


def deduplicate_events(events):
    """Remove duplicate normalized events, merging useful info."""
    seen = {}
    unique = []
    for ev in events:
        key = (
            ev.get("title", "").strip().lower(),
            (ev.get("location") or ev.get("address", "")).strip().lower(),
            (ev.get("date") or "")[:10],
        )
        if key not in seen:
            seen[key] = ev
            unique.append(ev)
        else:
            ex = seen[key]
            if ev.get("time") and ev.get("time") != ex.get("time"):
                if "Multiple times" not in str(ex.get("time")):
                    ex["time"] = f"{ex['time']} (Multiple times available)"
            if not ex.get("description") and ev.get("description"):
                ex["description"] = ev["description"]
            if not ex.get("organiser") and ev.get("organiser"):
                ex["organiser"] = ev["organiser"]
    return unique


def deduplicate_raw_events(raw_events, source_name):
    """Deduplicate raw events before normalization."""
    seen = {}
    unique = []
    for raw in raw_events:
        if source_name == "ticketmaster":
            key = (
                raw.get("title", "").lower(),
                raw.get("venue", "").lower(),
                (raw.get("date") or "")[:10],
            )
        elif source_name == "eventbrite":
            loc_raw = raw.get("Location", "")
            location = loc_raw.split("\n")[1] if "\n" in loc_raw else loc_raw
            date_raw = raw.get("Date & Time", "")
            date = date_raw.split("·")[0].strip(
            ) if "·" in date_raw else date_raw
            key = (raw.get("Title", "").lower(), location.lower(), date)
        else:
            title = (raw.get("title") or raw.get("Title") or "").lower()
            address_field = raw.get("address")
            location = (
                ", ".join(address_field) if isinstance(address_field, list) else
                (raw.get("location") or raw.get("venue") or address_field or "")
            ).lower()
            date_field = raw.get("date")
            date = (
                date_field.get("start_date", "") if isinstance(date_field, dict)
                else (date_field or raw.get("dates") or raw.get("Date & Time") or "")
            )
            key = (title, location, date)
        if key not in seen:
            seen[key] = raw
            unique.append(raw)
    return unique


def load_and_normalize():
    all_events = []
    total_files = len(NORMALIZERS)

    for i, (filename, normalizer) in enumerate(NORMALIZERS.items(), 1):
        path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(path):
            print(f"Missing file: {filename}")
            continue

        print(f"\nProcessing {filename} ({i}/{total_files})...")
        with open(path, "r", encoding="utf-8") as f:
            raw_events = json.load(f)
        print(f"Found {len(raw_events)} raw events...")

        unique_raw = deduplicate_raw_events(
            raw_events, filename.replace(".json", ""))
        print(
            f"Processing {len(unique_raw)} unique events (geocoding each)...")

        for j, raw in enumerate(unique_raw, 1):
            if j % 5 == 0:
                print(f"  Progress: {j}/{len(unique_raw)} events processed...")
            all_events.append(normalizer(raw))

        print(f"Completed {filename}: {len(unique_raw)} events normalized")

    return deduplicate_events(all_events)


if __name__ == "__main__":
    events = load_and_normalize()
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"Normalized {len(events)} events -> {OUTPUT_FILE}")
