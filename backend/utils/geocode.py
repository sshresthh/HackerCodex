import os
import requests
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


def geocode_google(address: str | None) -> dict:
    if not address or not GOOGLE_API_KEY:
        return {"lat": None, "lng": None}
    try:
        resp = requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={"address": address, "key": GOOGLE_API_KEY},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("results"):
            loc = data["results"][0]["geometry"]["location"]
            return {"lat": loc.get("lat"), "lng": loc.get("lng")}
    except Exception:
        pass
    return {"lat": None, "lng": None}


