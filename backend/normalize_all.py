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
        params = {"q": f"{address}, South Australia", "key": OPENCAGE_KEY, "limit": 1}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("results"):
            coords = data["results"][0]["geometry"]
            print(f"Geocoded: {address[:50]}... → {coords['lat']:.4f}, {coords['lng']:.4f}")
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

def normalize_ticketmaster(raw):
    # Parse organizer - take the first part before the first "|"
    organizer = raw.get("organizer", "")
    if "|" in organizer:
        organizer = organizer.split("|")[0].strip()
    
    # Clean up description - take the first part before "|" for cleaner display
    description = raw.get("description", "")
    if "|" in description and len(description) > 200:
        # Keep the main description, remove the "Please note" section for brevity
        description = description.split("|")[0].strip()
    
    # Convert empty string to None for consistency
    if not description:
        description = None
    if not organizer:
        organizer = None
    
    # Geocode the address
    address = raw.get("location", "")
    coords = geocode_opencage(address) if address else {"lat": None, "lng": None}
    
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
        "link": raw.get("link")
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
    """Remove duplicate events, keeping the first occurrence and combining time info."""
    seen = {}
    unique_events = []
    
    for event in events:
        # Normalize title and location for comparison
        title = event.get("title", "").strip().lower()
        location = (event.get("location") or event.get("address", "")).strip().lower()
        
        # Extract just the date part (ignore complex date formats)
        date_raw = event.get("date", "")
        if isinstance(date_raw, str):
            # Handle various date formats
            date_part = date_raw.split()[0] if date_raw else ""
            if "-" in date_part:  # YYYY-MM-DD format
                date_part = date_part
            elif "/" in date_part:  # MM/DD/YYYY format  
                date_part = date_part
            else:
                date_part = date_raw[:10] if len(date_raw) >= 10 else date_raw
        else:
            date_part = str(date_raw)
        
        # Create deduplication key
        key = (title, location, date_part)
        
        if key not in seen:
            # First occurrence - keep it
            seen[key] = event
            unique_events.append(event)
        else:
            # Duplicate found - merge time information if different
            existing = seen[key]
            current_time = event.get("time", "")
            existing_time = existing.get("time", "")
            
            # If times are different, combine them
            if current_time and existing_time and current_time != existing_time:
                if "Multiple times" not in str(existing_time):
                    existing["time"] = f"{existing_time} (Multiple times available)"
            elif current_time and not existing_time:
                existing["time"] = f"{current_time} (Multiple times available)"
            
            # Prefer events with descriptions and organizers
            if not existing.get("description") and event.get("description"):
                existing["description"] = event["description"]
            if not existing.get("organiser") and event.get("organiser"):
                existing["organiser"] = event["organiser"]
    
    duplicates_removed = len(events) - len(unique_events)
    print(f"Deduplicated: {len(events)} → {len(unique_events)} unique events ({duplicates_removed} duplicates removed)")
    return unique_events

def deduplicate_raw_events(raw_events, source_name):
    """Deduplicate raw events before normalization to save API calls."""
    seen = {}
    unique_raw = []
    
    for raw in raw_events:
        # Create key based on source-specific fields
        if source_name == "ticketmaster":
            title = raw.get("title", "").strip().lower()
            venue = raw.get("venue", "").strip().lower()
            date = raw.get("date", "").split()[0] if raw.get("date") else ""
            key = (title, venue, date)
        elif source_name == "eventbrite":
            title = raw.get("Title", "").strip().lower()
            location_raw = raw.get("Location", "")
            location = location_raw.split("\n")[1] if "\n" in location_raw else location_raw.strip().lower()
            date_raw = raw.get("Date & Time", "")
            date = date_raw.split("·")[0].strip() if "·" in date_raw else date_raw.strip()
            key = (title, location, date)
        else:
            # For other sources, use generic approach
            title = (raw.get("title") or raw.get("Title") or "").strip().lower()
            
            # Handle address field which might be a list (Google Events) or string
            address_field = raw.get("address")
            if isinstance(address_field, list):
                location = ", ".join(address_field).strip().lower()
            else:
                location = (raw.get("location") or raw.get("venue") or address_field or "").strip().lower()
            
            date_field = raw.get("date")
            if isinstance(date_field, dict):
                date = date_field.get("start_date", "").strip()
            else:
                date = (date_field or raw.get("dates") or raw.get("Date & Time") or "").strip()
            
            key = (title, location, date)
        
        if key not in seen:
            seen[key] = raw
            unique_raw.append(raw)
    
    duplicates_removed = len(raw_events) - len(unique_raw)
    if duplicates_removed > 0:
        print(f"  Pre-deduplication: {len(raw_events)} → {len(unique_raw)} unique events ({duplicates_removed} duplicates removed)")
    
    return unique_raw

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
        
        # Deduplicate raw events BEFORE normalization (saves API calls!)
        source_name = filename.replace(".json", "")
        unique_raw = deduplicate_raw_events(raw_events, source_name)
        
        print(f"Processing {len(unique_raw)} unique events (geocoding each)...")
        
        for j, raw in enumerate(unique_raw, 1):
            if j % 5 == 0:  # Progress every 5 events (fewer now)
                print(f"  Progress: {j}/{len(unique_raw)} events processed...")
            evt = normalizer(raw)
            all_events.append(evt)
            
        print(f"Completed {filename}: {len(unique_raw)} events normalized")
    
    return all_events

if __name__ == "__main__":
    events = load_and_normalize()
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"Normalized {len(events)} events → {OUTPUT_FILE}")
