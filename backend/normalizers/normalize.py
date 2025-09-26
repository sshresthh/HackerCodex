def normalize_adelaidefestival(raw):
    return {
        "title": raw.get("title"),
        "date": raw.get("date"),
        "time": "TBD",
        "location": None,
        "address": raw.get("address"),
        "price": None,
        "description": raw.get("description"),
        "features": [],
        "organiser": "Adelaide Festival Centre",
        "category": "Festival/Arts",
        "source": "AdelaideFestival",
        "link": raw.get("link")
    }

def normalize_eventbrite(raw):
    # Parse date & time
    dt = raw.get("Date & Time", "")
    date, time = None, None
    if "·" in dt:
        parts = dt.split("·")
        date = parts[0].replace("Date and time", "").strip()
        time = parts[1].strip() if len(parts) > 1 else None

    # Location may contain multiple lines
    loc = raw.get("Location", "").split("\n")
    location = loc[1] if len(loc) > 1 else None
    address = loc[2] if len(loc) > 2 else None

    return {
        "title": raw.get("Title"),
        "date": date,
        "time": time,
        "location": location,
        "address": address,
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
    return {
        "title": raw.get("title"),
        "date": raw.get("date", {}).get("start_date"),
        "time": raw.get("date", {}).get("when"),
        "location": raw.get("address", [None])[0],
        "address": addr,
        "price": None,
        "description": raw.get("description"),
        "features": [],
        "organiser": None,
        "category": "General",
        "source": "GoogleEvents",
        "link": raw.get("link")
    }

def normalize_southaustralia(raw):
    return {
        "title": raw.get("title"),
        "date": raw.get("dates"),
        "time": "TBD",
        "location": raw.get("location"),
        "address": raw.get("full_address"),
        "price": raw.get("price"),
        "description": None,
        "features": raw.get("features", []),
        "organiser": None,
        "category": "Tourism",
        "source": "SouthAustralia",
        "link": raw.get("link")
    }

NORMALIZERS = {
    "adelaidefestival": normalize_adelaidefestival,
    "eventbrite": normalize_eventbrite,
    "google_events": normalize_google,
    "southaustralia": normalize_southaustralia,
}
