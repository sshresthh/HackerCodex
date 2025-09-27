import os
import json
import hashlib
from typing import Any, Dict, List
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(__file__), "scrapers", "data")
INPUT_FILE = os.path.join(DATA_DIR, "normalized_events.json")


def fnum(x):
    try:
        return float(x)
    except Exception:
        return None


def key(source, link, title, date, location):
    base = f"{source or ''}|{link or ''}|{title or ''}|{date or ''}|{location or ''}"
    return hashlib.sha256(base.encode()).hexdigest()


def to_row(e: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "title": e.get("title"),
        "description": e.get("description"),
        "date": e.get("date"),
        "time": e.get("time"),
        "location": e.get("location"),
        "address": e.get("address"),
        "lat": fnum(e.get("lat")),
        "lng": fnum(e.get("lng")),
        "price": e.get("price"),
        "features": e.get("features") or [],
        "organiser": e.get("organiser"),
        "category": e.get("category"),
        "source": e.get("source"),
        "link": e.get("link"),
        "source_link_hash": key(e.get("source"), e.get("link"), e.get("title"), e.get("date"), e.get("location")),
    }


def chunks(lst: List[Dict[str, Any]], n: int):
    for i in range(0, len(lst), n):
        yield lst[i: i + n]


def main():
    url = os.getenv("SUPABASE_URL")
    key_sb = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv(
        "SUPABASE_ANON_KEY")
    if not url or not key_sb:
        raise SystemExit(
            "Missing SUPABASE_URL or SUPABASE_*_KEY in environment")

    sb = create_client(url, key_sb)

    if not os.path.exists(INPUT_FILE):
        raise SystemExit(f"Missing {INPUT_FILE}")

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        events = json.load(f)

    # Build rows and de-duplicate by source_link_hash to avoid
    # "ON CONFLICT DO UPDATE command cannot affect row a second time" errors
    dedup = {}
    for e in events:
        r = to_row(e)
        # Skip rows without valid lat/lng
        if r.get("lat") is None or r.get("lng") is None:
            continue
        k = r.get("source_link_hash")
        if not k:
            continue
        # keep the first occurrence
        if k not in dedup:
            dedup[k] = r
    # Cross-source de-duplication: collapse items that are likely the same event
    # using a canonical fingerprint (title+date+rounded coords)

    def canon_key(row: Dict[str, Any]) -> str:
        t = (row.get("title") or "").strip().lower()
        d = (row.get("date") or "").strip().lower()
        lat = row.get("lat")
        lng = row.get("lng")
        try:
            latr = round(float(lat), 4) if lat is not None else None
            lngr = round(float(lng), 4) if lng is not None else None
        except Exception:
            latr, lngr = None, None
        return f"{t}|{d}|{latr}|{lngr}"

    canon_map: Dict[str, Dict[str, Any]] = {}
    for r in dedup.values():
        ck = canon_key(r)
        if ck not in canon_map:
            canon_map[ck] = r
    rows = list(canon_map.values())
    total = 0
    for batch in chunks(rows, 500):
        sb.table("events").upsert(
            batch, on_conflict="source_link_hash").execute()
        total += len(batch)
    print(f"Upserted {total} events")


if __name__ == "__main__":
    main()
