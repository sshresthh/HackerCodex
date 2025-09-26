from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from processor import process_image_with_openai, get_coordinates_from_location

app = FastAPI()


origins = [
    "https://hacker-codex.vercel.app",
    "http://localhost:5173",         
    "http://127.0.0.1:5173",       
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"], 
    allow_headers=["*"],
)


@app.post("/api/process-poster")
async def process_poster_endpoint(file: UploadFile = File(...), request: Request = None):
    """
    Process uploaded poster image and extract event data.
    """

    try:
        client = request.client.host if request and request.client else "unknown"
        print(
            f"[API] Incoming upload from {client}: filename={file.filename}, content_type={file.content_type}")
    except Exception:
        pass

    # read uploaded image file into memory
    image_content = await file.read()
    print(f"[API] Received bytes: {len(image_content)}")
    event_data = process_image_with_openai(image_content)

    if not event_data:
        raise HTTPException(
            status_code=500, detail="Failed to process image.")

    # get location string
    location_text = event_data.get("Location", "")
    print(f"[API] Extracted location: {location_text}")
    coordinates = get_coordinates_from_location(location_text)
    # merging coordinates into event data
    event_data.update(coordinates)

    # final JSON data
    print(f"[API] Responding with: {event_data}")
    return event_data


# test
@app.get("/api/test")
def read_root():
    return {"message": "Hello from Mapster.city"}
