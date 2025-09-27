from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from processor import process_image_with_openai, get_coordinates_from_location
from supabase import create_client
from dotenv import load_dotenv
from openai import OpenAI
import hashlib
import os

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5-mini")

aoai_client = None
if AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT:
    aoai_client = OpenAI(api_key=AZURE_OPENAI_KEY, base_url=f"{AZURE_OPENAI_ENDPOINT}openai/v1/")

def _float_or_none(x):
    try:
        return float(x)
    except Exception:
        return None

def _hash_key(source: str | None, link: str | None, title: str | None, date: str | None, location: str | None) -> str:
    base = f"{source or ''}|{link or ''}|{title or ''}|{date or ''}|{location or ''}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


@app.post("/api/process-poster")
async def process_poster_endpoint(file: UploadFile = File(...)):
    """Process uploaded poster image and extract event data."""

    image_content = await file.read()
    event_data = process_image_with_openai(image_content)

    if not event_data:
        raise HTTPException(status_code=500, detail="Failed to process image.")

    location_text = event_data.get("Location", "")
    coordinates = get_coordinates_from_location(location_text)
    event_data.update(coordinates)

    # Upsert to Supabase if configured
    lat = _float_or_none(event_data.get("Latitude"))
    lng = _float_or_none(event_data.get("Longitude"))

    row = {
        "title": event_data.get("Title") or None,
        "description": event_data.get("Description") or None,
        "date": event_data.get("Date") or None,
        "time": event_data.get("Time") or None,
        "location": event_data.get("Location") or None,
        "address": None,
        "lat": lat,
        "lng": lng,
        "price": None,
        "features": [],
        "organiser": event_data.get("Organizer") or None,
        "category": "Community",
        "source": event_data.get("Source") or "Community Poster",
        "link": None,
    }
    row["source_link_hash"] = _hash_key(row["source"], row["link"], row["title"], row["date"], row["location"])

    if supabase:
        supabase.table("events").upsert(row, on_conflict="source_link_hash").execute()

    return event_data


@app.get("/api/events")
def list_events(
    sw_lng: float = Query(...),
    sw_lat: float = Query(...),
    ne_lng: float = Query(...),
    ne_lat: float = Query(...),
    limit: int = Query(500, ge=1, le=1000),
):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured.")
    res = (
        supabase.table("events")
        .select("*")
        .gte("lng", sw_lng)
        .lte("lng", ne_lng)
        .gte("lat", sw_lat)
        .lte("lat", ne_lat)
        .limit(limit)
        .execute()
    )
    return res.data or []


@app.get("/api/test")
def read_root():
    return {"message": "Hello from Mapster.city"}
